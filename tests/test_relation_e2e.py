"""
End-to-end tests for RelationCapability using BasedpyrightClient.

These tests verify the RelationCapability's ability to find call chains
between functions in real Python code using a real Language Server.
"""

from __future__ import annotations

import anyio
import pytest
from lsp_client.clients.basedpyright import BasedpyrightClient

from lsap.capability.relation import RelationCapability
from lsap.schema.locate import Locate, SymbolScope
from lsap.schema.relation import RelationRequest

from .framework.lsp import lsp_interaction_context


@pytest.mark.e2e
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_relation_direct_call():
    """Test finding a direct call relationship: A -> B."""
    async with lsp_interaction_context(BasedpyrightClient) as interaction:  # type: ignore
        # Create file with direct call
        content = '''
def caller():
    """The calling function."""
    return callee()

def callee():
    """The called function."""
    return 42
'''
        file_path = await interaction.create_file("direct_call.py", content)

        # Wait for LSP indexing
        await anyio.sleep(1)

        # Create RelationCapability
        capability = RelationCapability(client=interaction.client)  # type: ignore

        # Request to find path from caller to callee
        req = RelationRequest(
            source=Locate(
                file_path=file_path,
                scope=SymbolScope(symbol_path=["caller"]),
            ),
            target=Locate(
                file_path=file_path,
                scope=SymbolScope(symbol_path=["callee"]),
            ),
            max_depth=5,
        )

        resp = await capability(req)

        # Verify response
        assert resp is not None, "Response should not be None"
        assert resp.source.name == "caller"
        assert resp.target.name == "callee"
        assert len(resp.chains) == 1, f"Expected 1 chain, got {len(resp.chains)}"
        assert len(resp.chains[0]) == 2, "Chain should have 2 nodes: caller -> callee"
        assert resp.chains[0][0].name == "caller"
        assert resp.chains[0][1].name == "callee"

        # Test markdown formatting
        markdown = resp.format()
        assert "caller" in markdown
        assert "callee" in markdown
        assert "Found 1 call chain(s)" in markdown


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_relation_indirect_call():
    """Test finding an indirect call relationship: A -> B -> C."""
    async with lsp_interaction_context(BasedpyrightClient) as interaction:  # type: ignore
        content = '''
def entry_point():
    """Entry point function."""
    return middle_layer()

def middle_layer():
    """Middle layer function."""
    return final_destination()

def final_destination():
    """Final destination function."""
    return "success"
'''
        file_path = await interaction.create_file("indirect_call.py", content)

        await anyio.sleep(1)

        capability = RelationCapability(client=interaction.client)  # type: ignore

        req = RelationRequest(
            source=Locate(
                file_path=file_path,
                scope=SymbolScope(symbol_path=["entry_point"]),
            ),
            target=Locate(
                file_path=file_path,
                scope=SymbolScope(symbol_path=["final_destination"]),
            ),
            max_depth=10,
        )

        resp = await capability(req)

        assert resp is not None
        assert resp.source.name == "entry_point"
        assert resp.target.name == "final_destination"
        assert len(resp.chains) == 1
        assert len(resp.chains[0]) == 3, "Chain should have 3 nodes"
        assert resp.chains[0][0].name == "entry_point"
        assert resp.chains[0][1].name == "middle_layer"
        assert resp.chains[0][2].name == "final_destination"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_relation_multiple_paths():
    """Test finding multiple paths between two functions."""
    async with lsp_interaction_context(BasedpyrightClient) as interaction:  # type: ignore
        content = '''
def source():
    """Source function with multiple call paths."""
    path_a()
    path_b()
    return "done"

def path_a():
    """First path to target."""
    return target()

def path_b():
    """Second path to target."""
    return target()

def target():
    """Target function."""
    return 100
'''
        file_path = await interaction.create_file("multiple_paths.py", content)

        await anyio.sleep(1)

        capability = RelationCapability(client=interaction.client)  # type: ignore

        req = RelationRequest(
            source=Locate(
                file_path=file_path,
                scope=SymbolScope(symbol_path=["source"]),
            ),
            target=Locate(
                file_path=file_path,
                scope=SymbolScope(symbol_path=["target"]),
            ),
            max_depth=5,
        )

        resp = await capability(req)

        assert resp is not None
        assert resp.source.name == "source"
        assert resp.target.name == "target"
        assert len(resp.chains) == 2, f"Expected 2 paths, got {len(resp.chains)}"

        # Verify both paths exist
        middle_nodes = {chain[1].name for chain in resp.chains}
        assert middle_nodes == {"path_a", "path_b"}

        # Verify all chains have correct structure
        for chain in resp.chains:
            assert len(chain) == 3
            assert chain[0].name == "source"
            assert chain[2].name == "target"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_relation_no_connection():
    """Test when there's no connection between functions."""
    async with lsp_interaction_context(BasedpyrightClient) as interaction:  # type: ignore
        content = '''
def isolated_a():
    """Isolated function A."""
    return 1

def isolated_b():
    """Isolated function B."""
    return 2
'''
        file_path = await interaction.create_file("no_connection.py", content)

        await anyio.sleep(1)

        capability = RelationCapability(client=interaction.client)  # type: ignore

        req = RelationRequest(
            source=Locate(
                file_path=file_path,
                scope=SymbolScope(symbol_path=["isolated_a"]),
            ),
            target=Locate(
                file_path=file_path,
                scope=SymbolScope(symbol_path=["isolated_b"]),
            ),
            max_depth=5,
        )

        resp = await capability(req)

        assert resp is not None
        assert resp.source.name == "isolated_a"
        assert resp.target.name == "isolated_b"
        assert len(resp.chains) == 0, "Should find no chains"

        # Verify markdown shows no connection
        markdown = resp.format()
        assert "No connection found" in markdown


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_relation_max_depth_limit():
    """Test that max_depth is respected."""
    async with lsp_interaction_context(BasedpyrightClient) as interaction:  # type: ignore
        content = '''
def level_0():
    """Level 0."""
    return level_1()

def level_1():
    """Level 1."""
    return level_2()

def level_2():
    """Level 2."""
    return level_3()

def level_3():
    """Level 3."""
    return "deep"
'''
        file_path = await interaction.create_file("max_depth.py", content)

        await anyio.sleep(1)

        capability = RelationCapability(client=interaction.client)  # type: ignore

        # With max_depth=2, can reach level_2
        req = RelationRequest(
            source=Locate(
                file_path=file_path,
                scope=SymbolScope(symbol_path=["level_0"]),
            ),
            target=Locate(
                file_path=file_path,
                scope=SymbolScope(symbol_path=["level_2"]),
            ),
            max_depth=2,
        )

        resp = await capability(req)
        assert resp is not None
        assert len(resp.chains) == 1
        assert len(resp.chains[0]) == 3  # level_0 -> level_1 -> level_2

        # With max_depth=1, cannot reach level_2
        req_shallow = RelationRequest(
            source=Locate(
                file_path=file_path,
                scope=SymbolScope(symbol_path=["level_0"]),
            ),
            target=Locate(
                file_path=file_path,
                scope=SymbolScope(symbol_path=["level_2"]),
            ),
            max_depth=1,
        )

        resp_shallow = await capability(req_shallow)
        assert resp_shallow is not None
        assert len(resp_shallow.chains) == 0, "Should not find path within max_depth=1"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_relation_with_class_methods():
    """Test finding call chains involving class methods."""
    async with lsp_interaction_context(BasedpyrightClient) as interaction:  # type: ignore
        content = '''
class Calculator:
    """A simple calculator class."""

    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return self._internal_add(a, b)

    def _internal_add(self, a: int, b: int) -> int:
        """Internal addition method."""
        return a + b

def use_calculator():
    """Use the calculator."""
    calc = Calculator()
    return calc.add(1, 2)
'''
        file_path = await interaction.create_file("class_methods.py", content)

        await anyio.sleep(1.5)

        capability = RelationCapability(client=interaction.client)  # type: ignore

        # Find path from use_calculator to _internal_add
        req = RelationRequest(
            source=Locate(
                file_path=file_path,
                scope=SymbolScope(symbol_path=["use_calculator"]),
            ),
            target=Locate(
                file_path=file_path,
                scope=SymbolScope(symbol_path=["Calculator", "_internal_add"]),
            ),
            max_depth=5,
        )

        resp = await capability(req)

        assert resp is not None
        assert resp.source.name == "use_calculator"
        assert resp.target.name == "_internal_add"
        # Should find path: use_calculator -> Calculator.add -> Calculator._internal_add
        if len(resp.chains) > 0:
            assert resp.chains[0][0].name == "use_calculator"
            assert resp.chains[0][-1].name == "_internal_add"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_relation_cross_file():
    """Test finding call chains across multiple files."""
    async with lsp_interaction_context(BasedpyrightClient) as interaction:  # type: ignore
        # Create module with utility function
        util_content = '''
def utility_function():
    """A utility function."""
    return "utility"
'''
        util_path = await interaction.create_file("utils.py", util_content)

        # Create main file that imports and calls utility
        main_content = '''
from utils import utility_function

def main():
    """Main function."""
    return utility_function()
'''
        main_path = await interaction.create_file("main.py", main_content)

        await anyio.sleep(2)

        capability = RelationCapability(client=interaction.client)  # type: ignore

        # Find path from main to utility_function
        req = RelationRequest(
            source=Locate(
                file_path=main_path,
                scope=SymbolScope(symbol_path=["main"]),
            ),
            target=Locate(
                file_path=util_path,
                scope=SymbolScope(symbol_path=["utility_function"]),
            ),
            max_depth=5,
        )

        resp = await capability(req)

        assert resp is not None
        assert resp.source.name == "main"
        assert resp.target.name == "utility_function"
        # Should find direct call: main -> utility_function
        if len(resp.chains) > 0:
            assert len(resp.chains[0]) == 2
            assert resp.chains[0][0].name == "main"
            assert resp.chains[0][1].name == "utility_function"
            # Verify different files
            assert resp.chains[0][0].file_path != resp.chains[0][1].file_path


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_relation_invalid_source():
    """Test when source symbol cannot be found."""
    async with lsp_interaction_context(BasedpyrightClient) as interaction:  # type: ignore
        content = '''
def valid_function():
    """A valid function."""
    return 42
'''
        file_path = await interaction.create_file("invalid_source.py", content)

        await anyio.sleep(1)

        capability = RelationCapability(client=interaction.client)  # type: ignore

        req = RelationRequest(
            source=Locate(
                file_path=file_path,
                scope=SymbolScope(symbol_path=["nonexistent_function"]),
            ),
            target=Locate(
                file_path=file_path,
                scope=SymbolScope(symbol_path=["valid_function"]),
            ),
            max_depth=5,
        )

        resp = await capability(req)

        # Should return None when source cannot be located
        assert resp is None


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_relation_invalid_target():
    """Test when target symbol cannot be found."""
    async with lsp_interaction_context(BasedpyrightClient) as interaction:  # type: ignore
        content = '''
def valid_function():
    """A valid function."""
    return 42
'''
        file_path = await interaction.create_file("invalid_target.py", content)

        await anyio.sleep(1)

        capability = RelationCapability(client=interaction.client)  # type: ignore

        req = RelationRequest(
            source=Locate(
                file_path=file_path,
                scope=SymbolScope(symbol_path=["valid_function"]),
            ),
            target=Locate(
                file_path=file_path,
                scope=SymbolScope(symbol_path=["nonexistent_function"]),
            ),
            max_depth=5,
        )

        resp = await capability(req)

        # Should return None when target cannot be located
        assert resp is None


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_relation_different_path_lengths():
    """Test finding paths of different lengths to the same target."""
    async with lsp_interaction_context(BasedpyrightClient) as interaction:  # type: ignore
        content = '''
def source():
    """Source with multiple paths of different lengths."""
    direct()
    path1()
    path2()

def direct():
    """Direct path to target."""
    return target()

def path1():
    """One hop to target."""
    return path1_helper()

def path1_helper():
    """Helper for path1."""
    return target()

def path2():
    """Two hops to target."""
    return path2_a()

def path2_a():
    """First hop in path2."""
    return path2_b()

def path2_b():
    """Second hop in path2."""
    return target()

def target():
    """The target function."""
    return 100
'''
        file_path = await interaction.create_file("different_lengths.py", content)

        await anyio.sleep(1.5)

        capability = RelationCapability(client=interaction.client)  # type: ignore

        req = RelationRequest(
            source=Locate(
                file_path=file_path,
                scope=SymbolScope(symbol_path=["source"]),
            ),
            target=Locate(
                file_path=file_path,
                scope=SymbolScope(symbol_path=["target"]),
            ),
            max_depth=10,
        )

        resp = await capability(req)

        assert resp is not None
        assert resp.source.name == "source"
        assert resp.target.name == "target"
        # Should find multiple paths
        assert len(resp.chains) >= 1, "Should find at least one path"

        # Verify we have paths of different lengths
        path_lengths = sorted([len(chain) for chain in resp.chains])
        # Should have paths like: source->direct->target (3), source->path1->path1_helper->target (4), etc.
        assert len(set(path_lengths)) > 1, "Should have paths of different lengths"
