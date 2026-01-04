# Base classes
from .abc import PaginatedRequest, PaginatedResponse, Request, Response

# Definition
from .definition import (
    DefinitionRequest,
    DefinitionResponse,
)

# Hover
from .hover import HoverRequest, HoverResponse

# Locate
from .locate import (
    HERE,
    LineScope,
    Locate,
    LocateRange,
    LocateRangeRequest,
    LocateRangeResponse,
    LocateRequest,
    LocateResponse,
    SymbolScope,
)

# Types
from .models import (
    Position,
    Range,
    Location,
    SymbolCodeInfo,
    SymbolDetailInfo,
    SymbolInfo,
    SymbolKind,
)

# Reference
from .reference import ReferenceItem, ReferenceRequest, ReferenceResponse

# Symbol
from .symbol import SymbolRequest, SymbolResponse

# Symbol outline
from .symbol_outline import (
    SymbolOutlineRequest,
    SymbolOutlineResponse,
)

# Workspace
from .workspace_symbol import (
    WorkspaceSymbolItem,
    WorkspaceSymbolRequest,
    WorkspaceSymbolResponse,
)

# Draft - Unified Hierarchy API
from .draft.hierarchy import (
    HierarchyEdge,
    HierarchyItem,
    HierarchyNode,
    HierarchyRequest,
    HierarchyResponse,
)

# Draft - Backward compatibility for Call Hierarchy
from .draft.call_hierarchy import (
    CallEdge,
    CallHierarchyItem,
    CallHierarchyNode,
    CallHierarchyRequest,
    CallHierarchyResponse,
)

# Draft - Backward compatibility for Type Hierarchy
from .draft.type_hierarchy import (
    TypeEdge,
    TypeHierarchyItem,
    TypeHierarchyNode,
    TypeHierarchyRequest,
    TypeHierarchyResponse,
)

# Draft - Completion
from .draft.completion import (
    CompletionItem,
    CompletionRequest,
    CompletionResponse,
)

# Draft - Diagnostics
from .draft.diagnostics import (
    Diagnostic,
    FileDiagnosticsRequest,
    FileDiagnosticsResponse,
    WorkspaceDiagnosticItem,
    WorkspaceDiagnosticsRequest,
    WorkspaceDiagnosticsResponse,
)

# Draft - Rename
from .draft.rename import (
    RenameDiff,
    RenameFileChange,
    RenameRequest,
    RenameResponse,
)

# Draft - Inlay Hints
from .draft.inlay_hint import (
    DecoratedContentResponse,
    InlayHintItem,
    InlayHintRequest,
    InlineValueItem,
    InlineValueRequest,
)

__all__ = [
    # Base classes
    "PaginatedRequest",
    "PaginatedResponse",
    "Request",
    "Response",
    # Definition
    "DefinitionRequest",
    "DefinitionResponse",
    # Hover
    "HoverRequest",
    "HoverResponse",
    # Locate
    "HERE",
    "LineScope",
    "Locate",
    "LocateRange",
    "LocateRangeRequest",
    "LocateRangeResponse",
    "LocateRequest",
    "LocateResponse",
    "SymbolScope",
    "Position",
    "Range",
    "Location",
    "SymbolCodeInfo",
    "SymbolDetailInfo",
    "SymbolInfo",
    "SymbolKind",
    # Reference
    "ReferenceItem",
    "ReferenceRequest",
    "ReferenceResponse",
    # Symbol
    "SymbolRequest",
    "SymbolResponse",
    # Symbol outline
    "SymbolOutlineRequest",
    "SymbolOutlineResponse",
    # Workspace
    "WorkspaceSymbolItem",
    "WorkspaceSymbolRequest",
    "WorkspaceSymbolResponse",
    # Draft - Unified Hierarchy API
    "HierarchyEdge",
    "HierarchyItem",
    "HierarchyNode",
    "HierarchyRequest",
    "HierarchyResponse",
    # Draft - Call Hierarchy (backward compatibility)
    "CallEdge",
    "CallHierarchyItem",
    "CallHierarchyNode",
    "CallHierarchyRequest",
    "CallHierarchyResponse",
    # Draft - Type Hierarchy (backward compatibility)
    "TypeEdge",
    "TypeHierarchyItem",
    "TypeHierarchyNode",
    "TypeHierarchyRequest",
    "TypeHierarchyResponse",
    # Draft - Completion
    "CompletionItem",
    "CompletionRequest",
    "CompletionResponse",
    # Draft - Diagnostics
    "Diagnostic",
    "FileDiagnosticsRequest",
    "FileDiagnosticsResponse",
    "WorkspaceDiagnosticItem",
    "WorkspaceDiagnosticsRequest",
    "WorkspaceDiagnosticsResponse",
    # Draft - Rename
    "RenameDiff",
    "RenameFileChange",
    "RenameRequest",
    "RenameResponse",
    # Draft - Inlay Hints
    "DecoratedContentResponse",
    "InlayHintItem",
    "InlayHintRequest",
    "InlineValueItem",
    "InlineValueRequest",
]
