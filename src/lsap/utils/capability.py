from lsp_client import Client
from lsp_client.protocol.capability import CapabilityProtocol

from lsap.exception import UnsupportedCapabilityError


def ensure_capability[C: CapabilityProtocol](
    client: Client, capability: type[C], *, error: str | None = None
) -> C:
    """Ensure that the client supports the specified capability.

    Args:
        client: The LSP client instance.
        capability: The capability protocol class to check against.
        error: Optional custom error message suffix.

    Returns:
        The client instance cast to the specified capability type.

    Raises:
        UnsupportedCapabilityError: If the client does not support the capability.
    """
    if not error:
        error = "This operation cannot be performed."

    if not isinstance(client, capability):
        raise UnsupportedCapabilityError(
            f"Client {type(client).__name__} does not support capabilities: {', '.join(capability.iter_methods())}."
            + error
        )

    return client
