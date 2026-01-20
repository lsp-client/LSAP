from pathlib import Path

import pytest

from lsap.capability.locate import LocateCapability
from lsap.schema.locate import LineScope, Locate, LocateRequest


class MockClient:
    async def read_file(self, file_path: Path) -> str:
        return "abc\ndef abc\nghi"


@pytest.mark.asyncio
async def test_locate_text_ambiguous():
    client = MockClient()
    capability = LocateCapability(client=client)  # type: ignore

    # "abc" appears twice: line 1 and line 2 (1-based)
    req = LocateRequest(
        locate=Locate(
            file_path=Path("test.py"),
            scope=LineScope(start_line=1, end_line=3),
            find="abc",
        )
    )

    resp = await capability(req)
    assert resp is not None
    assert resp.position.line == 1
    assert resp.position.character == 1


@pytest.mark.asyncio
async def test_locate_text_single_match():
    client = MockClient()
    capability = LocateCapability(client=client)  # type: ignore

    req = LocateRequest(
        locate=Locate(
            file_path=Path("test.py"),
            scope=LineScope(start_line=1, end_line=3),
            find="def",
        )
    )

    resp = await capability(req)
    assert resp is not None
    assert resp.position.line == 2
    assert resp.position.character == 1
