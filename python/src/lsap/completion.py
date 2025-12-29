from functools import cached_property
from typing import Protocol, cast, override, runtime_checkable

from attrs import Factory, define
from lsap_schema.completion import CompletionItem, CompletionRequest, CompletionResponse
from lsp_client.capability.request import (
    WithRequestCompletion,
    WithRequestDocumentSymbol,
)
from lsp_client.protocol import CapabilityClientProtocol
from lsprotocol.types import CompletionItemKind

from lsap.utils.pagination import paginate

from .abc import Capability
from .locate import LocateCapability
from .utils.cache import PaginationCache


@runtime_checkable
class CompletionClient(
    WithRequestCompletion,
    WithRequestDocumentSymbol,
    CapabilityClientProtocol,
    Protocol,
): ...


@define
class CompletionCapability(
    Capability[CompletionClient, CompletionRequest, CompletionResponse]
):
    _cache: PaginationCache[CompletionItem] = Factory(PaginationCache)

    @cached_property
    def locate(self) -> LocateCapability:
        return LocateCapability(client=self.client)

    @override
    async def __call__(self, req: CompletionRequest) -> CompletionResponse | None:
        async def fetcher() -> list[CompletionItem] | None:
            if not (loc_resp := await self.locate(req)):
                return None

            file_path, lsp_pos = loc_resp.file_path, loc_resp.position.to_lsp()
            lsp_items = await self.client.request_completion(
                file_path, lsp_pos, resolve=True
            )

            if not lsp_items:
                return []

            items = []
            for lsp_item in lsp_items:
                kind = "Unknown"
                if lsp_item.kind is not None:
                    kind = cast(CompletionItemKind, lsp_item.kind).name

                documentation = None
                if lsp_item.documentation:
                    if isinstance(lsp_item.documentation, str):
                        documentation = lsp_item.documentation
                    else:
                        documentation = lsp_item.documentation.value

                items.append(
                    CompletionItem(
                        label=lsp_item.label,
                        kind=kind,
                        detail=lsp_item.detail,
                        documentation=documentation,
                        insert_text=lsp_item.insert_text or lsp_item.label,
                    )
                )

            return items

        result = await paginate(req, self._cache, fetcher)
        if result is None:
            return None

        return CompletionResponse(
            items=result.items,
            start_index=req.start_index,
            max_items=req.max_items,
            total=result.total,
            has_more=result.has_more,
            pagination_id=result.pagination_id,
        )
