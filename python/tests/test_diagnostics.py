from pathlib import Path
from typing import Sequence

import pytest
from lsap_schema import FileDiagnosticsRequest
from lsprotocol.types import (
    Diagnostic as LSPDiagnostic,
    DiagnosticSeverity,
    Position as LSPPosition,
    Range as LSPRange,
)

from lsap.draft.diagnostics import DiagnosticsCapability


class MockDiagnosticsClient:
    async def request_diagnostics(
        self, file_path: Path
    ) -> Sequence[LSPDiagnostic] | None:
        if "main.py" in str(file_path):
            return [
                LSPDiagnostic(
                    range=LSPRange(
                        start=LSPPosition(line=0, character=0),
                        end=LSPPosition(line=0, character=5),
                    ),
                    message="Error message",
                    severity=DiagnosticSeverity.Error,
                ),
                LSPDiagnostic(
                    range=LSPRange(
                        start=LSPPosition(line=1, character=0),
                        end=LSPPosition(line=1, character=5),
                    ),
                    message="Warning message",
                    severity=DiagnosticSeverity.Warning,
                ),
            ]
        return None

    def as_uri(self, file_path: Path) -> str:
        return f"file://{file_path}"

    def from_uri(self, uri: str) -> Path:
        return Path(uri.replace("file://", ""))


@pytest.mark.asyncio
async def test_diagnostics():
    client = MockDiagnosticsClient()
    capability = DiagnosticsCapability(client=client)  # type: ignore

    req = FileDiagnosticsRequest(file_path=Path("main.py"), min_severity="Hint")
    resp = await capability(req)

    assert resp is not None
    assert len(resp.diagnostics) == 2
    assert resp.diagnostics[0].message == "Error message"
    assert resp.diagnostics[0].severity == "Error"
    assert resp.diagnostics[1].message == "Warning message"
    assert resp.diagnostics[1].severity == "Warning"


@pytest.mark.asyncio
async def test_diagnostics_filtering():
    client = MockDiagnosticsClient()
    capability = DiagnosticsCapability(client=client)  # type: ignore

    req = FileDiagnosticsRequest(file_path=Path("main.py"), min_severity="Error")
    resp = await capability(req)

    assert resp is not None
    assert len(resp.diagnostics) == 1
    assert resp.diagnostics[0].severity == "Error"


@pytest.mark.asyncio
async def test_diagnostics_pagination_id():
    client = MockDiagnosticsClient()
    capability = DiagnosticsCapability(client=client)  # type: ignore

    # First request
    req1 = FileDiagnosticsRequest(file_path=Path("main.py"), max_items=1)
    resp1 = await capability(req1)
    assert resp1 is not None
    assert len(resp1.diagnostics) == 1
    assert resp1.pagination_id is not None
    assert resp1.has_more is True

    # Second request using pagination_id
    req2 = FileDiagnosticsRequest(
        file_path=Path("main.py"),
        pagination_id=resp1.pagination_id,
        start_index=1,
        max_items=1,
    )
    # Mock client should not be called again
    resp2 = await capability(req2)
    assert resp2 is not None
    assert len(resp2.diagnostics) == 1
    assert resp2.diagnostics[0].message == "Warning message"
    assert resp2.has_more is False
    assert resp2.pagination_id is None
