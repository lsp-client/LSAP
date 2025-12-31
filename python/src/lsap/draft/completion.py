from functools import cached_property
from typing import Protocol, override, runtime_checkable

from attrs import Factory, define
from lsap_schema.draft.completion import (
    CompletionItem,
    CompletionRequest,
    CompletionResponse,
)
from lsp_client.capability.request import (
    WithRequestCompletion,
    WithRequestDocumentSymbol,
)
from lsp_client.protocol import CapabilityClientProtocol
from lsprotocol.types import CompletionItemKind

from lsap.abc import Capability
from lsap.locate import LocateCapability
from lsap.utils.cache import PaginationCache
from lsap.utils.pagination import paginate


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
                    if isinstance(lsp_item.kind, CompletionItemKind):
                        kind = lsp_item.kind.name
                    else:
                        # Handle case where it might be a raw integer
                        try:
                            kind = CompletionItemKind(lsp_item.kind).name
                        except ValueError:
                            kind = str(lsp_item.kind)

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
