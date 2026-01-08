from lsp_client.exception import LSPError


class LSAPError(LSPError):
    """Base exception for all LSAP errors."""


class AmbiguousError(LSAPError):
    """Raised when an operation is ambiguous."""


class NotFoundError(LSAPError):
    """Raised when something is not found."""


class UnsupportedCapabilityError(LSAPError):
    """Raised when a capability is not supported by the client."""
