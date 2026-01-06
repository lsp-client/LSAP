from __future__ import annotations

import re
import uuid
from collections.abc import Iterator, Sequence
from functools import cached_property
from pathlib import Path
from typing import Protocol, runtime_checkable

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
from lsp_client.utils.types import lsp_type

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


type AnyTextEdit = (
    lsp_type.TextEdit | lsp_type.AnnotatedTextEdit | lsp_type.SnippetTextEdit
)


@define
class RenameCapability(Capability[RenameClient, RenameRequest, RenameResponse]):
    _preview_cache: dict[str, lsp_type.WorkspaceEdit] = Factory(dict)

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
        return None

    async def _preview(self, req: RenamePreviewRequest) -> RenamePreviewResponse | None:
        if not (loc := await self.locate(req)):
            return None

        path, pos = loc.file_path, loc.position.to_lsp()
        prepare = await self.client.request_prepare_rename(path, pos)
        if not prepare:
            return None

        old_name = await self._get_old_name(path, pos, prepare)
        edit = await self.client.request_rename_edits(path, pos, req.new_name)
        if not edit:
            return None

        rid = str(uuid.uuid4())
        self._preview_cache[rid] = edit
        changes = await self._to_changes(edit)

        return RenamePreviewResponse(
            request=req,
            rename_id=rid,
            old_name=old_name,
            new_name=req.new_name,
            total_files=len(changes),
            total_occurrences=sum(len(c.diffs) for c in changes),
            changes=changes,
        )

    async def _execute(self, req: RenameExecuteRequest) -> RenameExecuteResponse | None:
        edit = self._preview_cache.get(req.rename_id)
        if not edit or not (loc := await self.locate(req)):
            return None

        path, pos = loc.file_path, loc.position.to_lsp()
        prepare = await self.client.request_prepare_rename(path, pos)
        if not prepare:
            return None

        old_name = await self._get_old_name(path, pos, prepare)
        if req.exclude_files:
            edit = self._filter_edit(edit, set(req.exclude_files))

        changes = await self._to_changes(edit)
        await self.client.apply_workspace_edit(edit)
        self._preview_cache.pop(req.rename_id, None)

        return RenameExecuteResponse(
            request=req,
            old_name=old_name,
            new_name=req.new_name,
            total_files=len(changes),
            total_occurrences=sum(len(c.diffs) for c in changes),
            changes=changes,
        )

    async def _get_old_name(
        self, path: Path, pos: lsp_type.Position, res: lsp_type.PrepareRenameResult
    ) -> str:
        match res:
            case lsp_type.PrepareRenamePlaceholder(placeholder=p):
                return p
            case lsp_type.Range() as r:
                content = await self.client.read_file(path)
                if s := DocumentReader(content).read(r):
                    return s.exact_content
            case _:
                content = await self.client.read_file(path)
                return self._extract_word(content, pos)
        raise ValueError(f"Cannot extract old name from {res}")

    def _extract_word(self, content: str, pos: lsp_type.Position) -> str:
        lines = content.splitlines()
        if pos.line >= len(lines):
            raise ValueError(f"Line {pos.line} out of range")
        line = lines[pos.line]
        for m in re.finditer(r"\w+", line):
            if m.start() <= pos.character < m.end():
                return m.group()
        raise ValueError(f"No word at {pos.line}:{pos.character}")

    def _iter_edit(
        self, edit: lsp_type.WorkspaceEdit
    ) -> Iterator[tuple[str, Sequence[AnyTextEdit]]]:
        if edit.document_changes:
            for c in edit.document_changes:
                if isinstance(c, lsp_type.TextDocumentEdit):
                    yield c.text_document.uri, c.edits
        elif edit.changes:
            yield from edit.changes.items()

    def _filter_edit(
        self, edit: lsp_type.WorkspaceEdit, exclude: set[Path]
    ) -> lsp_type.WorkspaceEdit:
        if edit.document_changes:
            edit.document_changes = [
                c
                for c in edit.document_changes
                if not (
                    isinstance(c, lsp_type.TextDocumentEdit)
                    and self.client.from_uri(c.text_document.uri) in exclude
                )
            ]
        elif edit.changes:
            edit.changes = {
                u: e
                for u, e in edit.changes.items()
                if self.client.from_uri(u) not in exclude
            }
        return edit

    async def _to_changes(self, edit: lsp_type.WorkspaceEdit) -> list[RenameFileChange]:
        changes = []
        for uri, edits in self._iter_edit(edit):
            diffs = []
            content = await self.client.read_file(
                self.client.from_uri(uri, relative=False)
            )
            reader = DocumentReader(content)
            for e in edits:
                text = (
                    e.snippet.value
                    if isinstance(e, lsp_type.SnippetTextEdit)
                    else e.new_text
                )
                if s := reader.read(e.range):
                    diffs.append(
                        RenameDiff(
                            line=e.range.start.line + 1,
                            original=s.exact_content,
                            modified=text,
                        )
                    )
            if diffs:
                changes.append(
                    RenameFileChange(file_path=self.client.from_uri(uri), diffs=diffs)
                )
        return changes
