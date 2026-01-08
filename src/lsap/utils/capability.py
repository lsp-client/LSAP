from lsp_client import Client
from lsp_client.protocol.capability import CapabilityProtocol

from lsap.exception import UnsupportedCapabilityError


def ensure_capability[C: CapabilityProtocol](
    client: Client, capability: type[C], *, error: str | None = None
) -> C:
    if not error:
        error = "This operation cannot be performed."

    if not isinstance(client, capability):
        raise UnsupportedCapabilityError(
            f"Client {type(client).__name__} does not support capabilities: {', '.join(capability.iter_methods())}."
            + error
        )

    return client
