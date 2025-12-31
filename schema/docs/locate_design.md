# Locate Module Design Document

## Background

Most LSP (Language Server Protocol) capabilities require a precise code `Position` or `Range`. For LLM Agents, providing exact line and column numbers is difficult—Agents typically understand code based on semantics rather than precise character offsets.

### Problems with Traditional Approaches

**Option A: Direct Line/Column Specification**
```json
{"line": 42, "character": 15}
```
- Difficult for Agents to accurately calculate column numbers.
- Position becomes invalid after minor code changes.
- Lacks semantic expressiveness.

**Option B: Symbol Path Only**
```json
{"symbol_path": ["MyClass", "my_method"]}
```
- Can only locate symbol declarations.
- Cannot locate specific positions inside a symbol.
- Cannot handle non-symbol locations (e.g., string literals, comments).

## Design Goals

1. **Semantic-First**: Allow Agents to describe positions in a natural way.
2. **Precise & Controllable**: Reach character-level precision when needed.
3. **Comprehensive Coverage**: Support positioning requirements for all LSP `textDocument` capabilities.
4. **Robust & Fault-Tolerant**: Positioning remains valid after minor code changes.

## Core Concept: Two-Stage Positioning

```
Position = Scope (Narrowing down) + Find (Precise locating)
```

### Stage 1: Scope

Narrows the search area from the entire file to a specific region:

| Scope Type | Description | Typical Scenario |
|-----------|------|---------|
| `SymbolScope` | Code range of a symbol | Locating inside a specific function/class |
| `LineScope` | Line number or line range | Locating based on diagnostic information |
| `None` | Entire file | Global search for a text pattern |

### Stage 2: Find

Precise location within the Scope using a text pattern:

```python
find = "self.<HERE>value = value"
#           ^^^^^^ <HERE> marks the exact position
```

**`<HERE>` Marker Rules:**
- With `<HERE>`: Locates at the marker position.
- Without `<HERE>`: Locates at the start of the matched text.
- `find` is `None`: Uses the "natural position" of the Scope.
- Custom marker: Use `marker` field when source contains literal `<HERE>`.

```python
# Default marker
Locate(file_path="foo.py", find="self.<HERE>value")

# Custom marker when source contains "<HERE>"
Locate(file_path="foo.py", find="x = <|>value", marker="<|>")
```

## Position Resolution Rules

| Scope | Find | Resolution Result |
|-------|------|---------|
| `SymbolScope` | `None` | Position of the symbol's declared name |
| `SymbolScope` | With `<HERE>` | Marked position within the symbol body |
| `SymbolScope` | Without `<HERE>` | Start of matched text within the symbol body |
| `LineScope` | `None` | First non-whitespace character of the line |
| `LineScope` | With `<HERE>` | Marked position within the line |
| `LineScope` | Without `<HERE>` | Start of matched text within the line |
| `None` | With `<HERE>` | Global search, marked position |
| `None` | Without `<HERE>` | Global search, start of matched text |
| `None` | `None` | ❌ Invalid, validation failure |

## LSP Capability Mapping

### Capabilities Requiring Position

| LSP Capability | Positioning Need | Locate Usage |
|---------|---------|------------|
| `textDocument/definition` | Identifier position | `SymbolScope` or `find="<HERE>identifier"` |
| `textDocument/references` | Symbol declaration position | `SymbolScope(symbol_path=[...])` |
| `textDocument/rename` | Symbol declaration position | `SymbolScope(symbol_path=[...])` |
| `textDocument/hover` | Any identifier | `find="<HERE>target"` |
| `textDocument/completion` | Trigger point | `find="obj.<HERE>"` |
| `textDocument/signatureHelp` | Inside parentheses | `find="func(<HERE>"` |

### Capabilities Requiring Range

| LSP Capability | Positioning Need | LocateRange Usage |
|---------|---------|-----------------|
| `textDocument/codeAction` | Selected code range | `SymbolScope` or `find="selected text"` |
| `textDocument/formatting` | Formatting range | `SymbolScope` to select the entire symbol |

## Usage Examples

### 1. Find All References of a Symbol

```python
# Locate the declaration of class MyClass
Locate(
    file_path="models.py",
    scope=SymbolScope(symbol_path=["MyClass"])
)
```

The resolver treats `SymbolScope` as the declaration position of the class name `MyClass` in the source code, suitable for `references`, `rename`, etc.

### 2. Get Hover Information for a Variable

```python
# Locate the 'result' variable within the 'process' function
Locate(
    file_path="utils.py",
    scope=SymbolScope(symbol_path=["process"]),
    find="return <HERE>result"
)
```

First narrows down to the `process` function body, then searches for `return result` within it, positioning at the start of `result`.

### 3. Trigger Code Completion

```python
# Locate the position after 'self.'
Locate(
    file_path="service.py",
    find="self.<HERE>"
)
```

Global search for `self.`, positioning right after the dot to trigger member completion.

### 4. Get Code Actions

```python
# Select the entire function body
LocateRange(
    file_path="handlers.py",
    scope=SymbolScope(symbol_path=["handle_request"])
)

# Or select a specific code snippet
LocateRange(
    file_path="handlers.py",
    find="if error:\n    raise Exception(error)"
)
```

## Design Decision Record

### Q1: Why is Scope optional?

In some cases, the Agent knows the text pattern to search for but isn't sure which symbol it belongs to. Allowing `scope=None` enables file-wide searching.

```python
# Agent knows the code snippet but not the containing function
Locate(file_path="main.py", find="TODO: <HERE>fix this")
```

### Q2: Why is `<HERE>` optional?

Often, locating at the start of the matched text is sufficient:

```python
# Locate the call site of deprecated_func
Locate(file_path="old.py", find="deprecated_func(")
```

Forcing `<HERE>` everywhere would increase the cognitive load on the Agent.

### Q3: Why does SymbolScope without Find locate the declaration?

LSP's `references` and `rename` operations require the position of the symbol's **declared name**, not the start of the symbol body. This is the most common requirement for symbol positioning, making it the most sensible default.

```python
# This location can be used directly for find references
Locate(file_path="mod.py", scope=SymbolScope(symbol_path=["MyClass"]))
#                                                         ^^^^^^^
#                                                   Locates at "MyClass"
```

### Q4: Why a separate LocateRange?

`Position` and `Range` are distinct concepts:
- `Position`: A single point, used for hover, definition, completion.
- `Range`: An interval, used for codeAction, formatting.

While a `Range` can be constructed from two `Position`s, they represent different semantic operations. Modeling them separately is clearer.

### Q6: What if source code contains literal `<HERE>`?

The `marker` field allows customization:

```python
# Source contains "<HERE>" as actual code
Locate(file_path="parser.py", find="token = <|>HERE", marker="<|>")
```

This keeps the marker-based positioning intuitive without requiring the Agent to calculate offsets.

### Q7: Text matching rules in Find?

- Matching is **literal**, not regular expression.
- Matching **ignores whitespace differences** (to be confirmed in implementation).
- Returns the **first match** within the Scope.
- If multiple matches exist, the Agent can provide more context in `find` to disambiguate.

## Future Considerations

### Multiple Matches

When `find` has multiple matches within a Scope, the current design returns the first one. Future extensions could include:

```python
find: str | None = None
find_index: int = 0  # Return the N-th match
```

### Fuzzy Matching

To improve fault tolerance after code refactoring:

```python
find: str | None = None
fuzzy: bool = False  # Enable fuzzy matching
```

### Reverse Positioning

Generating a `Locate` description from a `Position`/`Range` to explain a location to the Agent:

```python
def describe_position(file: Path, pos: Position) -> Locate:
    """Generates a human-readable position description"""
    ...
```
