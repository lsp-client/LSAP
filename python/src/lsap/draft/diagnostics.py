from __future__ import annotations

from typing import Protocol, override, runtime_checkable

from attrs import Factory, define
from lsap_schema import (
    Diagnostic,
    FileDiagnosticsRequest,
    FileDiagnosticsResponse,
)
from lsap_schema import Position, Range
from lsp_client.capability.request.pull_diagnostic import WithRequestPullDiagnostic
from lsprotocol.types import DiagnosticSeverity

from ..abc import Capability, ClientProtocol
from ..utils.cache import PaginationCache
from ..utils.pagination import paginate


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
    _cache: PaginationCache[Diagnostic] = Factory(PaginationCache)

    @override
    async def __call__(
        self, req: FileDiagnosticsRequest
    ) -> FileDiagnosticsResponse | None:
        async def fetcher() -> list[Diagnostic] | None:
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
            return diagnostics

        result = await paginate(req, self._cache, fetcher)
        if result is None:
            return None

        return FileDiagnosticsResponse(
            file_path=req.file_path,
            diagnostics=result.items,
            total=result.total,
            start_index=req.start_index,
            max_items=req.max_items,
            has_more=result.has_more,
            pagination_id=result.pagination_id,
        )
