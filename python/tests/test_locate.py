from pathlib import Path

import pytest
from lsap_schema.locate import LocateRequest, LocateText

from lsap.error import AmbiguousError
from lsap.locate import (
    LocateCapability,
)


class MockClient:
    def read_file(self, file_path: Path) -> str:
        return "abc\ndef abc\nghi"


@pytest.mark.asyncio
async def test_locate_text_ambiguous():
    client = MockClient()
    capability = LocateCapability(client=client)  # type: ignore

    # "abc" appears twice: line 0 and line 1
    req = LocateRequest(
        locate=LocateText(
            file_path=Path("test.py"),
            line=(0, 1),
            find="abc",
        )
    )

    with pytest.raises(AmbiguousError) as excinfo:
        await capability(req)

    assert "Multiple matches for 'abc'" in str(excinfo.value)


@pytest.mark.asyncio
async def test_locate_text_single_match():
    client = MockClient()
    capability = LocateCapability(client=client)  # type: ignore

    req = LocateRequest(
        locate=LocateText(
            file_path=Path("test.py"),
            line=(0, 1),
            find="def",
            find_end="start",
        )
    )

    resp = await capability(req)
    assert resp is not None
    assert resp.position.line == 2
    assert resp.position.character == 1
