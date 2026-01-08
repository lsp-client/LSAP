from __future__ import annotations

from collections.abc import Sequence
from fnmatch import fnmatch
from functools import cached_property
from pathlib import Path
from typing import override

import asyncer
from attrs import define
from lsp_client.capability.request import WithRequestRename
from lsp_client.protocol import CapabilityClientProtocol
from lsp_client.utils.types import lsp_type
from lsp_client.utils.workspace_edit import (
    AnyTextEdit,
    get_edit_text,
    iter_text_document_edits,
)

from lsap.schema.rename import (
    RenameDiff,
    RenameExecuteRequest,
    RenameExecuteResponse,
    RenameFileChange,
    RenamePreviewRequest,
    RenamePreviewResponse,
)
from lsap.utils.cache import LRUCache
from lsap.utils.capability import ensure_capability
from lsap.utils.document import DocumentReader
from lsap.utils.id import generate_short_id

from .abc import Capability
from .locate import LocateCapability


@define
class CachedRename:
    edit: lsp_type.WorkspaceEdit
    old_name: str
    new_name: str


_preview_cache: LRUCache[str, CachedRename] = LRUCache()


def _get_old_name(
    reader: DocumentReader,
    pos: lsp_type.Position,
    res: lsp_type.PrepareRenameResult,
) -> str:
    match res:
        case lsp_type.Range() as lsp_range:
            if snippet := reader.read(lsp_range):
                return snippet.exact_content
        case lsp_type.PrepareRenamePlaceholder(placeholder=placeholder):
            return placeholder
        case lsp_type.PrepareRenameDefaultBehavior():
            return _extract_word(reader, pos)

    raise ValueError("Unknown PrepareRenameResult type")


def _extract_word(reader: DocumentReader, pos: lsp_type.Position) -> str:
    if word := reader.word_at(pos):
        return word
    raise ValueError(f"No word at {pos.line}:{pos.character}")


def _matches_exclude_patterns(
    path: Path, patterns: Sequence[str], workspace_root: Path
) -> bool:
    """Check if path matches any of the exclude patterns."""
    # Get path relative to workspace root for matching
    try:
        rel_path = path.relative_to(workspace_root)
    except ValueError:
        # If path is not under workspace root, use as-is
        rel_path = path

    rel_str = rel_path.as_posix()

    for pattern in patterns:
        # Support both Unix-style path separators and glob patterns
        pattern_normalized = str(pattern).replace("\\", "/")

        # Try PEP 428 Path.match() for glob patterns
        if rel_path.match(pattern_normalized):
            return True

        # Also try matching just the filename
        if fnmatch(rel_path.name, pattern_normalized):
            return True

        # Try exact match on relative path string
        if rel_str == pattern_normalized:
            return True

    return False


def _filter_edit(
    client: CapabilityClientProtocol,
    edit: lsp_type.WorkspaceEdit,
    exclude_patterns: Sequence[str],
) -> lsp_type.WorkspaceEdit:
    workspace_root = client.from_uri(client.as_uri(Path(".")), relative=False)

    def should_exclude(uri: str) -> bool:
        path = client.from_uri(uri, relative=False)
        return _matches_exclude_patterns(path, exclude_patterns, workspace_root)

    if edit.document_changes:
        filtered: list[
            lsp_type.TextDocumentEdit
            | lsp_type.CreateFile
            | lsp_type.RenameFile
            | lsp_type.DeleteFile
        ] = []
        for change in edit.document_changes:
            match change:
                case lsp_type.TextDocumentEdit(text_document=doc):
                    if not should_exclude(doc.uri):
                        filtered.append(change)
                case lsp_type.CreateFile(uri=uri) | lsp_type.DeleteFile(uri=uri):
                    if not should_exclude(uri):
                        filtered.append(change)
                case lsp_type.RenameFile(old_uri=old_uri, new_uri=new_uri):
                    if not should_exclude(old_uri) and not should_exclude(new_uri):
                        filtered.append(change)

        edit.document_changes = filtered
    elif edit.changes:
        edit.changes = {
            uri: text_edits
            for uri, text_edits in edit.changes.items()
            if not should_exclude(uri)
        }
    return edit


@define
class RenamePreviewCapability(Capability[RenamePreviewRequest, RenamePreviewResponse]):
    @cached_property
    def locate(self) -> LocateCapability:
        return LocateCapability(self.client)

    @override
    async def __call__(self, req: RenamePreviewRequest) -> RenamePreviewResponse | None:
        if not (locate := await self.locate(req)):
            return None

        path, pos = locate.file_path, locate.position.to_lsp()
        content = await self.client.read_file(path)
        reader = DocumentReader(content)

        prepare = await ensure_capability(
            self.client, WithRequestRename
        ).request_prepare_rename(path, pos)
        if not prepare:
            return None

        old_name = _get_old_name(reader, pos, prepare)
        edit = await ensure_capability(
            self.client, WithRequestRename
        ).request_rename_edits(path, pos, req.new_name)
        if not edit:
            return None

        rid = generate_short_id()
        _preview_cache.put(
            rid, CachedRename(edit=edit, old_name=old_name, new_name=req.new_name)
        )
        changes = await self._to_changes(edit, readers={path: reader})

        return RenamePreviewResponse(
            request=req,
            rename_id=rid,
            old_name=old_name,
            new_name=req.new_name,
            total_files=len(changes),
            total_occurrences=sum(
                len(edits) for _, edits in iter_text_document_edits(edit)
            ),
            changes=changes,
        )

    async def _to_changes(
        self,
        edit: lsp_type.WorkspaceEdit,
        *,
        readers: dict[Path, DocumentReader] | None = None,
    ) -> list[RenameFileChange]:
        soon_changes: list[asyncer.SoonValue[RenameFileChange | None]] = []
        async with asyncer.create_task_group() as tg:
            for uri, text_edits in iter_text_document_edits(edit):
                path = self.client.from_uri(uri, relative=False)
                reader = (readers or {}).get(path)
                soon_changes.append(
                    tg.soonify(self._to_file_change)(uri, text_edits, reader=reader)
                )
        return [change for soon in soon_changes if (change := soon.value)]

    async def _to_file_change(
        self,
        uri: str,
        edits: Sequence[AnyTextEdit],
        *,
        reader: DocumentReader | None = None,
    ) -> RenameFileChange | None:
        if reader is None:
            content = await self.client.read_file(
                self.client.from_uri(uri, relative=False)
            )
            reader = DocumentReader(content)

        diffs: list[RenameDiff] = []
        for edit in edits:
            start, end = edit.range.start, edit.range.end
            line_raw = reader.get_line(start.line, keepends=True)
            if line_raw is None:
                continue

            original_line = line_raw.rstrip("\r\n")
            new_text = get_edit_text(edit)

            if start.line == end.line:
                modified_line = (
                    line_raw[: start.character] + new_text + line_raw[end.character :]
                ).rstrip("\r\n")
            else:
                modified_line = new_text

            diffs.append(
                RenameDiff(
                    line=start.line + 1,
                    original=original_line,
                    modified=modified_line,
                )
            )

        if diffs:
            return RenameFileChange(file_path=self.client.from_uri(uri), diffs=diffs)
        return None


@define
class RenameExecuteCapability(Capability[RenameExecuteRequest, RenameExecuteResponse]):
    @override
    async def __call__(self, req: RenameExecuteRequest) -> RenameExecuteResponse | None:
        cached = _preview_cache.get(req.rename_id)
        if not cached:
            return None

        edit = cached.edit
        old_name = cached.old_name
        new_name = cached.new_name

        if req.exclude_files:
            edit = _filter_edit(self.client, edit, req.exclude_files)

        total_occurrences = sum(
            len(edits) for _, edits in iter_text_document_edits(edit)
        )
        changes = await self._to_changes(edit)
        await ensure_capability(
            self.client,
            WithRequestRename,
        ).apply_workspace_edit(edit)
        _preview_cache.pop(req.rename_id)

        return RenameExecuteResponse(
            request=req,
            old_name=old_name,
            new_name=new_name,
            total_files=len(changes),
            total_occurrences=total_occurrences,
            changes=changes,
        )

    async def _to_changes(
        self,
        edit: lsp_type.WorkspaceEdit,
        *,
        readers: dict[Path, DocumentReader] | None = None,
    ) -> list[RenameFileChange]:
        soon_changes: list[asyncer.SoonValue[RenameFileChange | None]] = []
        async with asyncer.create_task_group() as tg:
            for uri, text_edits in iter_text_document_edits(edit):
                path = self.client.from_uri(uri, relative=False)
                reader = (readers or {}).get(path)
                soon_changes.append(
                    tg.soonify(self._to_file_change)(uri, text_edits, reader=reader)
                )
        return [change for soon in soon_changes if (change := soon.value)]

    async def _to_file_change(
        self,
        uri: str,
        edits: Sequence[AnyTextEdit],
        *,
        reader: DocumentReader | None = None,
    ) -> RenameFileChange | None:
        if reader is None:
            content = await self.client.read_file(
                self.client.from_uri(uri, relative=False)
            )
            reader = DocumentReader(content)

        diffs: list[RenameDiff] = []
        for edit in edits:
            start, end = edit.range.start, edit.range.end
            line_raw = reader.get_line(start.line, keepends=True)
            if line_raw is None:
                continue

            original_line = line_raw.rstrip("\r\n")
            new_text = get_edit_text(edit)

            if start.line == end.line:
                modified_line = (
                    line_raw[: start.character] + new_text + line_raw[end.character :]
                ).rstrip("\r\n")
            else:
                modified_line = new_text

            diffs.append(
                RenameDiff(
                    line=start.line + 1,
                    original=original_line,
                    modified=modified_line,
                )
            )

        if diffs:
            return RenameFileChange(file_path=self.client.from_uri(uri), diffs=diffs)
        return None
