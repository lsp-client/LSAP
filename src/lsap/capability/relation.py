from __future__ import annotations

from collections import deque
from functools import cached_property
from pathlib import Path
from typing import override

from attrs import define
from lsp_client.capability.request import WithRequestCallHierarchy
from lsprotocol.types import (
    CallHierarchyItem,
    CallHierarchyOutgoingCallsParams,
)

from lsap.schema.locate import LocateRequest
from lsap.schema.relation import ChainNode, RelationRequest, RelationResponse
from lsap.utils.capability import ensure_capability

from .abc import Capability
from .locate import LocateCapability


@define
class RelationCapability(Capability[RelationRequest, RelationResponse]):
    @cached_property
    def locate(self) -> LocateCapability:
        return LocateCapability(self.client)

    @override
    async def __call__(self, req: RelationRequest) -> RelationResponse | None:
        # Resolve source symbol
        source_req = LocateRequest(locate=req.source)
        if not (source_loc := await self.locate(source_req)):
            return None

        # Resolve target symbol
        target_req = LocateRequest(locate=req.target)
        if not (target_loc := await self.locate(target_req)):
            return None

        # Get CallHierarchyItems for source and target
        call_hierarchy = ensure_capability(self.client, WithRequestCallHierarchy)

        source_items = await call_hierarchy.prepare_call_hierarchy(
            source_loc.file_path, source_loc.position.to_lsp()
        )
        if not source_items:
            return None

        target_items = await call_hierarchy.prepare_call_hierarchy(
            target_loc.file_path, target_loc.position.to_lsp()
        )
        if not target_items:
            return None

        # For simplicity, use the first (primary) symbol if multiple exist
        # This handles cases like overloaded functions or template instantiations
        # TODO: Consider searching paths for all source-target combinations if needed
        source_node = self._to_chain_node(source_items[0])
        target_node = self._to_chain_node(target_items[0])

        # Find all paths from source to target
        chains = await self._find_paths(
            call_hierarchy, source_items[0], target_items[0], req.max_depth
        )

        return RelationResponse(
            request=req,
            source=source_node,
            target=target_node,
            chains=chains,
        )

    def _to_chain_node(self, item: CallHierarchyItem) -> ChainNode:
        """Convert CallHierarchyItem to ChainNode"""
        file_path = Path(self.client.from_uri(item.uri, relative=False))
        return ChainNode(
            name=item.name,
            kind=item.kind.name if hasattr(item.kind, "name") else str(item.kind),
            file_path=file_path,
            detail=item.detail,
        )

    async def _find_paths(
        self,
        call_hierarchy: WithRequestCallHierarchy,
        source: CallHierarchyItem,
        target: CallHierarchyItem,
        max_depth: int,
    ) -> list[list[ChainNode]]:
        """
        Find all paths from source to target using BFS.

        Returns a list of chains, where each chain is a list of ChainNodes
        representing a path from source to target.
        """
        target_key = self._item_key(target)
        found_chains: list[list[ChainNode]] = []

        # BFS queue: (current_item, path_so_far, depth)
        queue: deque[tuple[CallHierarchyItem, list[ChainNode], int]] = deque()
        queue.append((source, [self._to_chain_node(source)], 0))

        # Track visited nodes to avoid cycles
        visited: set[str] = set()

        while queue:
            current_item, path, depth = queue.popleft()
            current_key = self._item_key(current_item)

            # Check if we've reached the target
            if current_key == target_key:
                found_chains.append(path)
                continue

            # Skip if we've exceeded max depth
            if depth >= max_depth:
                continue

            # Skip if already visited (cycle detection)
            if current_key in visited:
                continue
            visited.add(current_key)

            # Get outgoing calls from current item
            outgoing_calls = (
                await call_hierarchy._request_call_hierarchy_outgoing_calls(
                    CallHierarchyOutgoingCallsParams(item=current_item)
                )
            )

            if not outgoing_calls:
                continue

            # Add each outgoing call to the queue
            for call in outgoing_calls:
                next_item = call.to
                next_key = self._item_key(next_item)
                # Skip if already visited to prevent redundant queue entries
                if next_key not in visited:
                    next_node = self._to_chain_node(next_item)
                    next_path = path + [next_node]
                    queue.append((next_item, next_path, depth + 1))

        return found_chains

    def _item_key(self, item: CallHierarchyItem) -> str:
        """Generate a unique key for a CallHierarchyItem"""
        file_path = self.client.from_uri(item.uri, relative=False)
        return f"{file_path}:{item.range.start.line}:{item.range.start.character}:{item.name}"
