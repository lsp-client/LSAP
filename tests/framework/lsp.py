from __future__ import annotations

import tempfile
from collections.abc import AsyncGenerator, Sequence
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import attrs
from lsp_client.capability.request.completion import WithRequestCompletion
from lsp_client.capability.request.definition import WithRequestDefinition
from lsp_client.capability.request.document_symbol import WithRequestDocumentSymbol
from lsp_client.capability.request.hover import WithRequestHover
from lsp_client.capability.request.reference import WithRequestReferences
from lsp_client.client.abc import Client
from lsp_client.utils.types import Position, Range, lsp_type

type LspResponse[R] = R | None


@attrs.define
class LspInteraction[C: Client]:
    client: C
    workspace_root: Path

    @property
    def resolved_workspace(self) -> Path:
        """Get resolved workspace path for path comparisons."""
        return self.workspace_root.resolve()

    def full_path(self, relative_path: str) -> Path:
        # Return the original path (not resolved) for file operations
        # This is important for symlinked fixtures
        return self.workspace_root / relative_path

    def full_path_resolved(self, relative_path: str) -> Path:
        """Return resolved path for comparison with pyrefly responses."""
        return (self.workspace_root / relative_path).resolve()

    async def create_file(self, relative_path: str, content: str) -> Path:
        path = self.full_path(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    async def request_definition(
        self, relative_path: str, line: int, column: int
    ) -> DefinitionAssertion:
        assert isinstance(self.client, WithRequestDefinition)
        path = self.full_path(relative_path)
        resp = await self.client.request_definition(
            file_path=path,
            position=Position(line=line, character=column),
        )
        return DefinitionAssertion(self, resp)

    async def request_hover(
        self, relative_path: str, line: int, column: int
    ) -> HoverAssertion:
        assert isinstance(self.client, WithRequestHover)
        path = self.full_path(relative_path)
        resp = await self.client.request_hover(
            file_path=path,
            position=Position(line=line, character=column),
        )
        return HoverAssertion(self, resp)

    async def request_completion(
        self, relative_path: str, line: int, column: int
    ) -> CompletionAssertion:
        assert isinstance(self.client, WithRequestCompletion)
        path = self.full_path(relative_path)
        resp = await self.client.request_completion(
            file_path=path,
            position=Position(line=line, character=column),
        )
        return CompletionAssertion(self, resp)

    async def request_references(
        self, relative_path: str, line: int, column: int
    ) -> ReferencesAssertion:
        assert isinstance(self.client, WithRequestReferences)
        path = self.full_path(relative_path)
        resp = await self.client.request_references(
            file_path=path,
            position=Position(line=line, character=column),
        )
        return ReferencesAssertion(self, resp)

    async def request_document_symbols(
        self, relative_path: str
    ) -> DocumentSymbolsAssertion:
        assert isinstance(self.client, WithRequestDocumentSymbol)
        path = self.full_path(relative_path)
        resp = await self.client.request_document_symbol(file_path=path)
        return DocumentSymbolsAssertion(self, resp)


@attrs.define
class DefinitionAssertion:
    interaction: LspInteraction[Any]
    response: (
        lsp_type.Location
        | Sequence[lsp_type.Location]
        | Sequence[lsp_type.LocationLink]
        | None
    )

    def expect_definition(
        self,
        relative_path: str,
        start_line: int,
        start_col: int,
        end_line: int,
        end_col: int,
    ) -> None:
        assert self.response is not None, "Definition response is None"

        # Use resolved path for comparison with pyrefly responses
        expected_path = self.interaction.full_path_resolved(relative_path)
        expected_range = Range(
            start=Position(line=start_line, character=start_col),
            end=Position(line=end_line, character=end_col),
        )

        match self.response:
            case lsp_type.Location() as loc:
                actual_path = Path(
                    self.interaction.client.from_uri(loc.uri, relative=False)
                )
                # Compare using resolved paths to handle symlinks properly
                actual_resolved = actual_path.resolve()
                expected_resolved = expected_path.resolve()
                assert actual_resolved == expected_resolved, (
                    f"Expected resolved path {expected_resolved}, got {actual_resolved}"
                )
                assert loc.range == expected_range
            case list() | Sequence() as locs:
                found = False
                for loc in locs:
                    if isinstance(loc, lsp_type.Location):
                        actual_path = Path(
                            self.interaction.client.from_uri(loc.uri, relative=False)
                        )
                        actual_range = loc.range
                    elif isinstance(loc, lsp_type.LocationLink):
                        actual_path = Path(
                            self.interaction.client.from_uri(
                                loc.target_uri, relative=False
                            )
                        )
                        actual_range = loc.target_selection_range
                    else:
                        continue

                    # Compare using resolved paths to handle symlinks
                    actual_resolved = actual_path.resolve()
                    expected_resolved = expected_path.resolve()
                    path_match = actual_resolved == expected_resolved

                    if path_match and actual_range == expected_range:
                        found = True
                        break

                assert found, (
                    f"Definition not found at {expected_path}:{expected_range}"
                )
            case _:
                raise TypeError(
                    f"Unexpected definition response type: {type(self.response)}"
                )

        match self.response:
            case lsp_type.Location() as loc:
                actual_path = Path(
                    self.interaction.client.from_uri(loc.uri, relative=False)
                )
                # Pyrefly may return resolved paths
                # Compare using resolved paths to handle symlinks properly
                actual_resolved = actual_path.resolve()
                expected_resolved = expected_path.resolve()
                assert actual_resolved == expected_resolved, (
                    f"Expected resolved path {expected_resolved}, got {actual_resolved}"
                )
                assert loc.range == expected_range
            case list() | Sequence() as locs:
                found = False
                for loc in locs:
                    if isinstance(loc, lsp_type.Location):
                        actual_path = Path(
                            self.interaction.client.from_uri(loc.uri, relative=False)
                        )
                        actual_range = loc.range
                    elif isinstance(loc, lsp_type.LocationLink):
                        actual_path = Path(
                            self.interaction.client.from_uri(
                                loc.target_uri, relative=False
                            )
                        )
                        actual_range = loc.target_selection_range
                    else:
                        continue

                    # Compare using resolved paths to handle symlinks
                    actual_resolved = actual_path.resolve()
                    expected_resolved = expected_path.resolve()
                    path_match = actual_resolved == expected_resolved

                    if path_match and actual_range == expected_range:
                        found = True
                        break

                assert found, (
                    f"Definition not found at {expected_path}:{expected_range}"
                )
            case _:
                raise TypeError(
                    f"Unexpected definition response type: {type(self.response)}"
                )

        match self.response:
            case lsp_type.Location() as loc:
                actual_path = Path(
                    self.interaction.client.from_uri(loc.uri, relative=False)
                )
                # Pyrefly may return resolved paths, so we need to handle symlinks
                # Try to resolve both paths and compare
                try:
                    actual_resolved = actual_path.resolve()
                    expected_resolved = expected_path.resolve()
                    assert actual_resolved == expected_resolved, (
                        f"Expected resolved path {expected_resolved}, got {actual_resolved}"
                    )
                except ValueError:
                    # Fallback to relative path comparison if resolve fails
                    actual_rel = actual_path.relative_to(
                        self.interaction.workspace_root
                    )
                    expected_rel = expected_path.relative_to(
                        self.interaction.workspace_root
                    )
                    assert actual_rel == expected_rel, (
                        f"Expected path {expected_rel}, got {actual_rel}"
                    )
                assert loc.range == expected_range
            case list() | Sequence() as locs:
                found = False
                for loc in locs:
                    if isinstance(loc, lsp_type.Location):
                        actual_path = Path(
                            self.interaction.client.from_uri(loc.uri, relative=False)
                        )
                        actual_range = loc.range
                    elif isinstance(loc, lsp_type.LocationLink):
                        actual_path = Path(
                            self.interaction.client.from_uri(
                                loc.target_uri, relative=False
                            )
                        )
                        actual_range = loc.target_selection_range
                    else:
                        continue

                    # Pyrefly may return resolved paths, so we need to handle symlinks
                    try:
                        actual_resolved = actual_path.resolve()
                        expected_resolved = expected_path.resolve()
                        path_match = actual_resolved == expected_resolved
                    except ValueError:
                        # Fallback to relative path comparison
                        try:
                            actual_rel = actual_path.relative_to(
                                self.interaction.workspace_root
                            )
                            expected_rel = expected_path.relative_to(
                                self.interaction.workspace_root
                            )
                            path_match = actual_rel == expected_rel
                        except ValueError:
                            path_match = False

                    if path_match and actual_range == expected_range:
                        found = True
                        break

                assert found, (
                    f"Definition not found at {expected_path}:{expected_range}"
                )
            case _:
                raise TypeError(
                    f"Unexpected definition response type: {type(self.response)}"
                )

        match self.response:
            case lsp_type.Location() as loc:
                actual_path = Path(
                    self.interaction.client.from_uri(loc.uri, relative=False)
                )
                # Compare using relative paths to handle symlinks
                try:
                    actual_rel = actual_path.relative_to(
                        self.interaction.workspace_root
                    )
                    expected_rel = expected_path.relative_to(
                        self.interaction.workspace_root
                    )
                    assert actual_rel == expected_rel, (
                        f"Expected path {expected_rel}, got {actual_rel}"
                    )
                except ValueError:
                    # Fallback to absolute path comparison
                    assert actual_path.resolve() == expected_path.resolve(), (
                        f"Expected path {expected_path}, got {actual_path}"
                    )
                assert loc.range == expected_range
            case list() | Sequence() as locs:
                found = False
                for loc in locs:
                    if isinstance(loc, lsp_type.Location):
                        actual_path = Path(
                            self.interaction.client.from_uri(loc.uri, relative=False)
                        )
                        actual_range = loc.range
                    elif isinstance(loc, lsp_type.LocationLink):
                        actual_path = Path(
                            self.interaction.client.from_uri(
                                loc.target_uri, relative=False
                            )
                        )
                        actual_range = loc.target_selection_range
                    else:
                        continue

                    # Compare using relative paths to handle symlinks
                    try:
                        actual_rel = actual_path.relative_to(
                            self.interaction.workspace_root
                        )
                        expected_rel = expected_path.relative_to(
                            self.interaction.workspace_root
                        )
                        path_match = actual_rel == expected_rel
                    except ValueError:
                        # Fallback to absolute path comparison
                        path_match = actual_path.resolve() == expected_path.resolve()

                    if path_match and actual_range == expected_range:
                        found = True
                        break

                assert found, (
                    f"Definition not found at {expected_path}:{expected_range}"
                )
            case _:
                raise TypeError(
                    f"Unexpected definition response type: {type(self.response)}"
                )

        match self.response:
            case lsp_type.Location() as loc:
                actual_path = Path(
                    self.interaction.client.from_uri(loc.uri, relative=False)
                )
                # Compare using relative paths to handle symlinks
                try:
                    actual_rel = actual_path.relative_to(
                        self.interaction.workspace_root
                    )
                    expected_rel = expected_path.relative_to(
                        self.interaction.workspace_root
                    )
                    assert actual_rel == expected_rel, (
                        f"Expected path {expected_rel}, got {actual_rel}"
                    )
                except ValueError:
                    # Fallback to absolute path comparison
                    assert actual_path.resolve() == expected_path.resolve(), (
                        f"Expected path {expected_path}, got {actual_path}"
                    )
                assert loc.range == expected_range
            case list() | Sequence() as locs:
                found = False
                for loc in locs:
                    if isinstance(loc, lsp_type.Location):
                        actual_path = Path(
                            self.interaction.client.from_uri(loc.uri, relative=False)
                        )
                        actual_range = loc.range
                    elif isinstance(loc, lsp_type.LocationLink):
                        actual_path = Path(
                            self.interaction.client.from_uri(
                                loc.target_uri, relative=False
                            )
                        )
                        actual_range = loc.target_selection_range
                    else:
                        continue

                    # Compare using relative paths to handle symlinks
                    try:
                        actual_rel = actual_path.relative_to(
                            self.interaction.workspace_root
                        )
                        expected_rel = expected_path.relative_to(
                            self.interaction.workspace_root
                        )
                        path_match = actual_rel == expected_rel
                    except ValueError:
                        # Fallback to absolute path comparison
                        path_match = actual_path.resolve() == expected_path.resolve()

                    if path_match and actual_range == expected_range:
                        found = True
                        break

                assert found, (
                    f"Definition not found at {expected_path}:{expected_range}"
                )
            case _:
                raise TypeError(
                    f"Unexpected definition response type: {type(self.response)}"
                )

        match self.response:
            case lsp_type.Location() as loc:
                actual_path = Path(
                    self.interaction.client.from_uri(loc.uri, relative=False)
                )
                # Compare using relative paths to handle symlinks
                try:
                    actual_rel = actual_path.relative_to(
                        self.interaction.workspace_root
                    )
                    expected_rel = expected_path.relative_to(
                        self.interaction.workspace_root
                    )
                    assert actual_rel == expected_rel, (
                        f"Expected path {expected_rel}, got {actual_rel}"
                    )
                except ValueError:
                    # Fallback to absolute path comparison
                    assert actual_path.resolve() == expected_path.resolve(), (
                        f"Expected path {expected_path}, got {actual_path}"
                    )
                assert loc.range == expected_range
            case list() | Sequence() as locs:
                found = False
                for loc in locs:
                    if isinstance(loc, lsp_type.Location):
                        actual_path = Path(
                            self.interaction.client.from_uri(loc.uri, relative=False)
                        )
                        actual_range = loc.range
                    elif isinstance(loc, lsp_type.LocationLink):
                        actual_path = Path(
                            self.interaction.client.from_uri(
                                loc.target_uri, relative=False
                            )
                        )
                        actual_range = loc.target_selection_range
                    else:
                        continue

                    # Compare using relative paths to handle symlinks
                    try:
                        actual_rel = actual_path.relative_to(
                            self.interaction.workspace_root
                        )
                        expected_rel = expected_path.relative_to(
                            self.interaction.workspace_root
                        )
                        path_match = actual_rel == expected_rel
                    except ValueError:
                        # Fallback to absolute path comparison
                        path_match = actual_path.resolve() == expected_path.resolve()

                    if path_match and actual_range == expected_range:
                        found = True
                        break

                assert found, (
                    f"Definition not found at {expected_path}:{expected_range}"
                )
            case _:
                raise TypeError(
                    f"Unexpected definition response type: {type(self.response)}"
                )


@attrs.define
class HoverAssertion:
    interaction: LspInteraction[Any]
    response: lsp_type.MarkupContent | None

    def expect_content(self, pattern: str) -> None:
        assert self.response is not None, "Hover response is None"
        assert pattern in self.response.value, (
            f"Expected '{pattern}' in hover content, got '{self.response.value}'"
        )


@attrs.define
class CompletionAssertion:
    interaction: LspInteraction[Any]
    response: Sequence[lsp_type.CompletionItem]

    def expect_label(self, label: str) -> None:
        labels = [item.label for item in self.response]
        assert label in labels, (
            f"Expected completion label '{label}' not found in {labels}"
        )


@attrs.define
class ReferencesAssertion:
    interaction: LspInteraction[Any]
    response: Sequence[lsp_type.Location] | None

    def expect_reference(
        self,
        relative_path: str,
        start_line: int,
        start_col: int,
        end_line: int,
        end_col: int,
    ) -> None:
        assert self.response is not None, "References response is None"
        expected_path = self.interaction.full_path(relative_path)
        expected_range = Range(
            start=Position(line=start_line, character=start_col),
            end=Position(line=end_line, character=end_col),
        )

        found = False
        for loc in self.response:
            actual_path = self.interaction.client.from_uri(loc.uri, relative=False)
            if (
                Path(actual_path).resolve() == expected_path
                and loc.range == expected_range
            ):
                found = True
                break
        assert found, f"Reference not found at {expected_path}:{expected_range}"


@attrs.define
class DocumentSymbolsAssertion:
    interaction: LspInteraction[Any]
    response: (
        Sequence[lsp_type.SymbolInformation] | Sequence[lsp_type.DocumentSymbol] | None
    )
    _last_found_names: list[str] = attrs.field(factory=list, init=False)

    def expect_symbol(self, name: str, kind: lsp_type.SymbolKind | None = None) -> None:
        assert self.response is not None, "Document symbols response is None"

        def check_symbols(
            symbols: Sequence[lsp_type.SymbolInformation]
            | Sequence[lsp_type.DocumentSymbol],
            found_names: list[str],
        ) -> bool:
            for sym in symbols:
                if isinstance(sym, lsp_type.DocumentSymbol):
                    found_names.append(f"{sym.name} ({sym.kind})")
                    if sym.name == name and (kind is None or sym.kind == kind):
                        return True
                    if sym.children and check_symbols(sym.children, found_names):
                        return True
                elif isinstance(sym, lsp_type.SymbolInformation):
                    found_names.append(f"{sym.name} ({sym.kind})")
                    if sym.name == name and (kind is None or sym.kind == kind):
                        return True
            return False

        self._last_found_names = []
        if not check_symbols(self.response, self._last_found_names):
            print(f"Actually found: {self._last_found_names}")
            raise AssertionError(f"Symbol '{name}' not found")


@asynccontextmanager
async def lsp_interaction_context[C: Client](
    client_cls: type[C], workspace_root: Path | None = None, **client_kwargs: Any
) -> AsyncGenerator[LspInteraction[C], None]:
    if workspace_root is None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir).resolve()
            async with client_cls(workspace=root, **client_kwargs) as client:
                yield LspInteraction(client=client, workspace_root=root)
    else:
        # Use original path to preserve symlinks
        # This is important for test fixtures that are symlinked
        root = workspace_root
        async with client_cls(workspace=root, **client_kwargs) as client:
            yield LspInteraction(client=client, workspace_root=root)
