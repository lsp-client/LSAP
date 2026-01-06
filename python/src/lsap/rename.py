from __future__ import annotations

import re
import uuid
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Sequence

from attrs import Factory, define
from lsap_schema.rename import (
    RenameDiff,
    RenameExecuteRequest,
    RenameExecuteResponse,
    RenameFileChange,
    RenamePreviewRequest,
    RenamePreviewResponse,
    RenameRequest,
    RenameResponse,
)
from lsp_client.capability.request import WithRequestDocumentSymbol, WithRequestRename
from lsp_client.protocol import CapabilityClientProtocol
from lsprotocol.types import (
    AnnotatedTextEdit,
    Position,
    PrepareRenameDefaultBehavior,
    PrepareRenamePlaceholder,
    PrepareRenameResult,
    Range,
    SnippetTextEdit,
    TextDocumentEdit,
    TextEdit,
    WorkspaceEdit,
)

from .abc import Capability
from .locate import LocateCapability
from .utils.document import DocumentReader


@runtime_checkable
class RenameClient(
    WithRequestRename,
    WithRequestDocumentSymbol,
    CapabilityClientProtocol,
    Protocol,
): ...


@define
class RenameCapability(Capability[RenameClient, RenameRequest, RenameResponse]):
    _preview_cache: dict[str, WorkspaceEdit] = Factory(dict)

    @cached_property
    def locate(self) -> LocateCapability:
        return LocateCapability(self.client)

    async def __call__(self, req: RenameRequest) -> RenameResponse | None:
        match req.root:
            case RenamePreviewRequest() as preview:
                if resp := await self._preview(preview):
                    return RenameResponse(root=resp)
            case RenameExecuteRequest() as execute:
                if resp := await self._execute(execute):
                    return RenameResponse(root=resp)

    async def _preview(self, req: RenamePreviewRequest) -> RenamePreviewResponse | None:
        if not (loc_resp := await self.locate(req)):
            return None

        file_path, lsp_pos = loc_resp.file_path, loc_resp.position.to_lsp()

        prepare_result = await self.client.request_prepare_rename(file_path, lsp_pos)
        if not prepare_result:
            return None

        old_name = await self._extract_old_name(file_path, lsp_pos, prepare_result)

        workspace_edit = await self.client.request_rename_edits(
            file_path, lsp_pos, req.new_name
        )
        if not workspace_edit:
            return None

        rename_id = str(uuid.uuid4())
        self._preview_cache[rename_id] = workspace_edit

        changes = await self._workspace_edit_to_changes(workspace_edit)

        total_files = len(changes)
        total_occurrences = sum(len(fc.diffs) for fc in changes)

        return RenamePreviewResponse(
            request=req,
            rename_id=rename_id,
            old_name=old_name,
            new_name=req.new_name,
            total_files=total_files,
            total_occurrences=total_occurrences,
            changes=changes,
        )

    async def _execute(self, req: RenameExecuteRequest) -> RenameExecuteResponse | None:
        workspace_edit = self._preview_cache.get(req.rename_id)
        if not workspace_edit:
            return None

        if not (loc_resp := await self.locate(req)):
            return None

        file_path, lsp_pos = loc_resp.file_path, loc_resp.position.to_lsp()

        prepare_result = await self.client.request_prepare_rename(file_path, lsp_pos)
        if not prepare_result:
            return None

        old_name = await self._extract_old_name(file_path, lsp_pos, prepare_result)

        changes = await self._workspace_edit_to_changes(
            workspace_edit, exclude_files=req.exclude_files
        )

        if req.exclude_files:
            workspace_edit = self._filter_workspace_edit(
                workspace_edit, req.exclude_files
            )

        await self.client.apply_workspace_edit(workspace_edit)

        del self._preview_cache[req.rename_id]

        total_files = len(changes)
        total_occurrences = sum(len(fc.diffs) for fc in changes)

        return RenameExecuteResponse(
            request=req,
            old_name=old_name,
            new_name=req.new_name,
            total_files=total_files,
            total_occurrences=total_occurrences,
            changes=changes,
        )

    async def _extract_old_name(
        self, file_path: Path, position: Position, prepare_result: PrepareRenameResult
    ) -> str:
        match prepare_result:
            case PrepareRenamePlaceholder(placeholder=placeholder):
                return placeholder
            case Range():
                content = await self.client.read_file(file_path)
                reader = DocumentReader(content)
                if snippet := reader.read(prepare_result):
                    return snippet.exact_content
                raise ValueError(f"Cannot extract text from range: {prepare_result}")
            case PrepareRenameDefaultBehavior():
                content = await self.client.read_file(file_path)
                return self._extract_word_at_position(
                    content, position.line, position.character
                )

    def _extract_word_at_position(self, content: str, line: int, character: int) -> str:
        lines = content.split("\n")
        if line >= len(lines):
            raise ValueError(f"Line {line} out of range")

        line_text = lines[line]
        if character >= len(line_text):
            raise ValueError(f"Character {character} out of range on line {line}")

        for match in re.finditer(r"\w+", line_text):
            if match.start() <= character < match.end():
                return match.group()

        raise ValueError(f"No word found at position {line}:{character}")

    def _get_workspace_root(self) -> Path:
        workspace = self.client.get_workspace()
        if len(workspace) == 1:
            return next(iter(workspace.values())).path
        return Path.cwd()

    async def _process_text_edits(
        self,
        uri: str,
        edits: Sequence[TextEdit | AnnotatedTextEdit | SnippetTextEdit],
    ) -> list[RenameDiff]:
        """Process text edits and return diffs for a single file."""
        file_path = self.client.from_uri(uri, relative=False)
        content = await self.client.read_file(file_path)
        reader = DocumentReader(content)

        diffs: list[RenameDiff] = []
        for edit in edits:
            match edit:
                case SnippetTextEdit(range=edit_range, snippet=snippet):
                    new_text = snippet.value
                case (
                    TextEdit(range=edit_range, new_text=new_text)
                    | AnnotatedTextEdit(range=edit_range, new_text=new_text)
                ):
                    pass

            if not edit_range or new_text is None:
                continue

            line = edit_range.start.line + 1
            if snippet := reader.read(edit_range):
                diffs.append(
                    RenameDiff(
                        line=line,
                        original=snippet.exact_content,
                        modified=new_text,
                    )
                )
        return diffs

    async def _workspace_edit_to_changes(
        self,
        workspace_edit: WorkspaceEdit,
        *,
        exclude_files: list[Path] | None = None,
    ) -> list[RenameFileChange]:
        exclude_files = exclude_files or []
        workspace_root = self._get_workspace_root()
        exclude_set = {workspace_root / f for f in exclude_files}

        changes: list[RenameFileChange] = []

        if workspace_edit.document_changes:
            for change in workspace_edit.document_changes:
                match change:
                    case TextDocumentEdit(text_document=text_document, edits=edits):
                        uri = text_document.uri
                        file_path = self.client.from_uri(uri, relative=False)

                        if file_path in exclude_set:
                            continue

                        diffs = await self._process_text_edits(uri, edits)

                        if diffs:
                            changes.append(
                                RenameFileChange(
                                    file_path=self.client.from_uri(uri, relative=True),
                                    diffs=diffs,
                                )
                            )
                    case _:
                        continue

        elif workspace_edit.changes:
            for uri, edits in workspace_edit.changes.items():
                file_path = self.client.from_uri(uri, relative=False)

                if file_path in exclude_set:
                    continue

                diffs = await self._process_text_edits(uri, edits)

                if diffs:
                    changes.append(
                        RenameFileChange(
                            file_path=self.client.from_uri(uri, relative=True),
                            diffs=diffs,
                        )
                    )

        return changes

    def _filter_workspace_edit(
        self, workspace_edit: WorkspaceEdit, exclude_files: list[Path]
    ) -> WorkspaceEdit:
        workspace_root = self._get_workspace_root()
        exclude_set = {workspace_root / f for f in exclude_files}

        if workspace_edit.document_changes:
            filtered_changes = []
            for change in workspace_edit.document_changes:
                match change:
                    case TextDocumentEdit(text_document=text_document):
                        if (
                            self.client.from_uri(text_document.uri, relative=False)
                            not in exclude_set
                        ):
                            filtered_changes.append(change)
                    case _:
                        filtered_changes.append(change)
            workspace_edit.document_changes = filtered_changes

        elif workspace_edit.changes:
            filtered_changes = {
                uri: edits
                for uri, edits in workspace_edit.changes.items()
                if self.client.from_uri(uri, relative=False) not in exclude_set
            }
            workspace_edit.changes = filtered_changes

        return workspace_edit
