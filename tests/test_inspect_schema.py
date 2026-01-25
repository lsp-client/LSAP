from pathlib import Path
import pytest
from pydantic import ValidationError
from lsap.schema.draft.inspect import InspectRequest, InspectResponse, UsageExample
from lsap.schema.locate import Locate
from lsap.schema.models import (
    SymbolDetailInfo,
    Location,
    Position,
    Range,
    SymbolKind,
    SymbolInfo,
    CallHierarchy,
    CallHierarchyItem,
)


def test_inspect_request_defaults():
    """Test InspectRequest default values."""
    req = InspectRequest(locate=Locate(file_path=Path("test.py"), find="func"))
    assert req.include_examples == 3
    assert req.include_signature is True
    assert req.include_doc is True
    assert req.include_call_hierarchy is False
    assert req.include_external is False
    assert req.context_lines == 2


def test_inspect_request_validation():
    """Test InspectRequest field validation."""
    # Test include_examples range
    with pytest.raises(ValidationError):
        InspectRequest(
            locate=Locate(file_path=Path("test.py"), find="func"), include_examples=-1
        )
    with pytest.raises(ValidationError):
        InspectRequest(
            locate=Locate(file_path=Path("test.py"), find="func"), include_examples=21
        )

    # Test context_lines range
    with pytest.raises(ValidationError):
        InspectRequest(
            locate=Locate(file_path=Path("test.py"), find="func"), context_lines=-1
        )
    with pytest.raises(ValidationError):
        InspectRequest(
            locate=Locate(file_path=Path("test.py"), find="func"), context_lines=11
        )


def test_usage_example_model():
    """Test UsageExample model instantiation."""
    example = UsageExample(
        code="func('test')",
        location=Location(
            file_path=Path("main.py"),
            range=Range(
                start=Position(line=10, character=5),
                end=Position(line=10, character=15),
            ),
        ),
        context=SymbolInfo(
            name="caller",
            kind=SymbolKind.Function,
            file_path=Path("main.py"),
            range=Range(
                start=Position(line=5, character=1), end=Position(line=15, character=1)
            ),
            path=["caller"],
        ),
        call_pattern="func(arg)",
    )
    assert example.code == "func('test')"
    assert example.call_pattern == "func(arg)"
    assert example.context.name == "caller"


def test_inspect_response_serialization():
    """Test InspectResponse serialization and deserialization."""
    info = SymbolDetailInfo(
        name="my_func",
        kind=SymbolKind.Function,
        file_path=Path("test.py"),
        range=Range(
            start=Position(line=1, character=1), end=Position(line=5, character=1)
        ),
        path=["my_func"],
        hover="My function documentation",
    )

    example = UsageExample(
        code="my_func()",
        location=Location(
            file_path=Path("app.py"),
            range=Range(
                start=Position(line=2, character=1), end=Position(line=2, character=9)
            ),
        ),
    )

    resp = InspectResponse(
        info=info, signature="def my_func() -> None", examples=[example]
    )

    # Serialize to dict
    data = resp.model_dump()
    assert data["info"]["name"] == "my_func"
    assert len(data["examples"]) == 1
    assert data["signature"] == "def my_func() -> None"

    # Deserialize back
    resp2 = InspectResponse.model_validate(data)
    assert resp2.info.name == "my_func"
    assert resp2.signature == "def my_func() -> None"
    assert len(resp2.examples) == 1


def test_inspect_response_markdown_rendering():
    """Test InspectResponse.format('markdown') renders correctly."""
    info = SymbolDetailInfo(
        name="my_func",
        kind=SymbolKind.Function,
        file_path=Path("test.py"),
        range=Range(
            start=Position(line=1, character=1), end=Position(line=5, character=1)
        ),
        path=["my_func"],
        hover="My function documentation",
    )

    example = UsageExample(
        code="my_func()",
        location=Location(
            file_path=Path("app.py"),
            range=Range(
                start=Position(line=2, character=1), end=Position(line=2, character=9)
            ),
        ),
        context=SymbolInfo(
            name="main",
            kind=SymbolKind.Function,
            file_path=Path("app.py"),
            range=Range(
                start=Position(line=1, character=1), end=Position(line=10, character=1)
            ),
            path=["main"],
        ),
        call_pattern="my_func()",
    )

    call_hierarchy = CallHierarchy(
        incoming=[
            CallHierarchyItem(
                name="caller_func",
                kind=SymbolKind.Function,
                file_path=Path("caller.py"),
                range=Range(
                    start=Position(line=5, character=1),
                    end=Position(line=5, character=10),
                ),
                selection_range=Range(
                    start=Position(line=5, character=1),
                    end=Position(line=5, character=10),
                ),
            )
        ],
        outgoing=[],
    )

    resp = InspectResponse(
        info=info,
        signature="def my_func() -> None",
        examples=[example],
        call_hierarchy=call_hierarchy,
    )

    markdown = resp.format("markdown")

    assert "# Inspect: `my_func` (`function`)" in markdown
    assert "## Signature" in markdown
    assert "def my_func() -> None" in markdown
    assert "## Documentation" in markdown
    assert "My function documentation" in markdown
    assert "## Usage Examples" in markdown
    assert "### Example 1" in markdown
    assert "In `main` (`function`)" in markdown
    assert "Pattern: `my_func()`" in markdown
    assert "my_func()" in markdown
    assert "## Incoming Calls" in markdown
    assert "- `caller_func` (`function`)" in markdown
    assert "Use these examples to understand" in markdown
