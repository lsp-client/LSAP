from __future__ import annotations

from typing import Protocol, override, runtime_checkable

from attrs import Factory, define
from lsap_schema.diagnostics import (
    Diagnostic,
    FileDiagnosticsRequest,
    FileDiagnosticsResponse,
)
from lsap_schema.types import Position, Range
from lsp_client.capability.request.pull_diagnostic import WithRequestPullDiagnostic
from lsprotocol.types import DiagnosticSeverity

from .abc import Capability, ClientProtocol
from .utils.cache import PaginationCache


@runtime_checkable
class DiagnosticsClient(
    WithRequestPullDiagnostic,
    ClientProtocol,
    Protocol,
): ...


@define
class DiagnosticsCapability(
    Capability[DiagnosticsClient, FileDiagnosticsRequest, FileDiagnosticsResponse]
):
    _cache: PaginationCache[list[Diagnostic]] = Factory(PaginationCache)

    @override
    async def __call__(
        self, req: FileDiagnosticsRequest
    ) -> FileDiagnosticsResponse | None:
        pagination_id = req.pagination_id
        if pagination_id and (cached := self._cache.get(pagination_id)) is not None:
            diagnostics = cached
        else:
            lsp_diagnostics = await self.client.request_diagnostics(req.file_path)
            if lsp_diagnostics is None:
                return None

            severity_map = {
                "Error": DiagnosticSeverity.Error,
                "Warning": DiagnosticSeverity.Warning,
                "Information": DiagnosticSeverity.Information,
                "Hint": DiagnosticSeverity.Hint,
            }
            min_severity_val = severity_map[req.min_severity]

            diagnostics = []
            for d in lsp_diagnostics:
                severity = d.severity or DiagnosticSeverity.Error
                if severity <= min_severity_val:
                    diagnostics.append(
                        Diagnostic(
                            range=Range(
                                start=Position.from_lsp(d.range.start),
                                end=Position.from_lsp(d.range.end),
                            ),
                            severity=severity.name,
                            message=d.message,
                            source=d.source,
                            code=d.code if isinstance(d.code, (str, int)) else None,
                        )
                    )

            pagination_id = self._cache.put(diagnostics)

        start = req.start_index
        end = start + req.max_items if req.max_items else len(diagnostics)
        paginated_diagnostics = diagnostics[start:end]
        has_more = end < len(diagnostics)

        return FileDiagnosticsResponse(
            file_path=req.file_path,
            diagnostics=paginated_diagnostics,
            total=len(diagnostics),
            start_index=start,
            max_items=req.max_items,
            has_more=has_more,
            pagination_id=pagination_id if has_more else None,
        )
