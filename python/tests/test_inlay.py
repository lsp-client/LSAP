from pathlib import Path
import pytest
from lsprotocol.types import InlayHint, Position, Range
from lsap.protocol.inlay import InlayReadCapability, InlayReadRequest


class MockInlayClient:
    def read_file(self, file_path: Path) -> str:
        return "x = 1\ny = 2"

    async def request_inlay_hint(
        self, file_path: Path, range: Range
    ) -> list[InlayHint]:
        # Return hints in non-sorted order to test sorting
        return [
            InlayHint(
                position=Position(line=1, character=1),
                label=": int",
                padding_left=True,
                padding_right=True,
            ),
            InlayHint(
                position=Position(line=0, character=1),
                label=": int",
                padding_left=False,
                padding_right=False,
            ),
        ]

    def get_inlay_hint_label(self, hint: InlayHint) -> str:
        if isinstance(hint.label, str):
            return hint.label
        return "".join(part.value for part in hint.label)


@pytest.mark.asyncio
async def test_inlay_read():
    client = MockInlayClient()
    capability = InlayReadCapability(client=client)  # type: ignore

    req = InlayReadRequest(file_path=Path("test.py"))
    resp = await capability(req)

    assert resp is not None
    assert resp.content == "x: int = 1\ny : int  = 2"


@pytest.mark.asyncio
async def test_inlay_read_range():
    client = MockInlayClient()
    capability = InlayReadCapability(client=client)  # type: ignore

    # Range covering only the second line "y = 2"
    req = InlayReadRequest(
        file_path=Path("test.py"),
        range=Range(
            start=Position(line=1, character=0), end=Position(line=1, character=5)
        ),
    )
    resp = await capability(req)

    assert resp is not None
    # line 1: "y" (0) + " : int " + " = 2" (1-end) -> "y : int  = 2"
    assert resp.content == "y : int  = 2"


@pytest.mark.asyncio
async def test_inlay_read_empty():
    class EmptyClient:
        def read_file(self, file_path: Path) -> str:
            return ""

    client = EmptyClient()
    capability = InlayReadCapability(client=client)  # type: ignore
    req = InlayReadRequest(file_path=Path("empty.py"))
    resp = await capability(req)
    assert resp is not None
    assert resp.content == ""


@pytest.mark.asyncio
async def test_inlay_read_multiple_at_same_pos():
    class MultiHintClient:
        def read_file(self, file_path: Path) -> str:
            return "x"

        async def request_inlay_hint(
            self, file_path: Path, range: Range
        ) -> list[InlayHint]:
            return [
                InlayHint(position=Position(line=0, character=1), label=": A"),
                InlayHint(position=Position(line=0, character=1), label=": B"),
            ]

        def get_inlay_hint_label(self, hint: InlayHint) -> str:
            return str(hint.label)

    client = MultiHintClient()
    capability = InlayReadCapability(client=client)  # type: ignore
    req = InlayReadRequest(file_path=Path("test.py"))
    resp = await capability(req)
    assert resp is not None
    # x: A: B
    assert resp.content == "x: A: B"


@pytest.mark.asyncio
async def test_inlay_read_no_hints():
    class NoHintsClient:
        def read_file(self, file_path: Path) -> str:
            return "x = 1"

        async def request_inlay_hint(
            self, file_path: Path, range: Range
        ) -> list[InlayHint]:
            return []

    client = NoHintsClient()
    capability = InlayReadCapability(client=client)  # type: ignore
    req = InlayReadRequest(file_path=Path("test.py"))
    resp = await capability(req)
    assert resp is not None
    assert resp.content == "x = 1"
