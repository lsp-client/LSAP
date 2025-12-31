from __future__ import annotations

from typing import Literal, Protocol, override, runtime_checkable

from attrs import Factory, define
from lsap_schema.draft.diagnostics import (
    Diagnostic,
    FileDiagnosticsRequest,
    FileDiagnosticsResponse,
)
from lsap_schema.models import Position, Range
from lsp_client.capability.request import WithDocumentDiagnostic
from lsp_client.protocol import CapabilityClientProtocol
from lsprotocol.types import DiagnosticSeverity

from lsap.abc import Capability
from lsap.utils.cache import PaginationCache
from lsap.utils.pagination import paginate


@runtime_checkable
class DiagnosticsClient(WithDocumentDiagnostic, CapabilityClientProtocol, Protocol): ...


@define
class FileDiagnosticsCapability(
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

            severity_map: dict[
                DiagnosticSeverity, Literal["Error", "Warning", "Information", "Hint"]
            ] = {
                DiagnosticSeverity.Error: "Error",
                DiagnosticSeverity.Warning: "Warning",
                DiagnosticSeverity.Information: "Information",
                DiagnosticSeverity.Hint: "Hint",
            }

            items = []
            for d in lsp_diagnostics:
                severity: Literal["Error", "Warning", "Information", "Hint"] = (
                    "Information"
                )
                if d.severity is not None:
                    try:
                        severity = severity_map[DiagnosticSeverity(d.severity)]
                    except (KeyError, ValueError):
                        pass

                items.append(
                    Diagnostic(
                        range=Range(
                            start=Position.from_lsp(d.range.start),
                            end=Position.from_lsp(d.range.end),
                        ),
                        severity=severity,
                        message=d.message,
                        source=d.source,
                        code=d.code,
                    )
                )

            # Filter by min_severity
            severity_order = ["Hint", "Information", "Warning", "Error"]
            min_idx = severity_order.index(req.min_severity)
            items = [i for i in items if severity_order.index(i.severity) >= min_idx]

            return items

        result = await paginate(req, self._cache, fetcher)
        if result is None:
            return None

        return FileDiagnosticsResponse(
            file_path=req.file_path,
            diagnostics=result.items,
            start_index=req.start_index,
            max_items=req.max_items,
            total=result.total,
            has_more=result.has_more,
            pagination_id=result.pagination_id,
        )
