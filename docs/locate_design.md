# Locate Module Design Document

## Background

Most LSP (Language Server Protocol) capabilities require a precise code `Position` or `Range`. For LLM Agents, providing exact line and column numbers is difficult: Agents typically understand code based on semantics rather than precise character offsets.

### Problems with Traditional Approaches

**Option A: Direct Line/Column Specification** (Used by editors)

```json
{ "line": 42, "character": 15 }
```

- Difficult for Agents to accurately calculate column numbers.
- Position becomes invalid after minor code changes.
- Lacks semantic expressiveness.

**Option B: Symbol Path Only** (Used by most LSP tools like Serena, Claude Code, etc.)

```json
{ "symbol_path": ["MyClass", "my_method"] }
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

| Scope Type    | Description               | Typical Scenario                          |
| ------------- | ------------------------- | ----------------------------------------- |
| `SymbolScope` | Code range of a symbol    | Locating inside a specific function/class |
| `LineScope`   | Line number or line range | Locating based on diagnostic information  |
| `None`        | Entire file               | Global search for a text pattern          |

### Stage 2: Find

Precise location within the Scope using a text pattern:

```python
find = "self.<|>value = value"
#            ^^^ <|> marks the exact position
```

**Automatic Marker Detection Rules:**

- Markers use nested bracket notation: `<|>`, `<<|>>`, `<<<|>>>`, etc.
- The system automatically detects the marker with the deepest nesting level that appears exactly once
- With marker: Locates at the marker position
- Without marker: Locates at the start of the matched text
- `find` is `None`: Uses the "natural position" of the Scope

```python
# Basic marker
Locate(file_path="foo.py", find="self.<|>value")

# When <|> appears multiple times, use deeper nesting
Locate(file_path="foo.py", find="x = <|> + y <<|>> z")
# Will automatically use <<|>> as the position marker

# String syntax for concise location specification
locate_str = "foo.py:MyClass.my_method@self.<|>"
locate = parse_locate_string(locate_str)
```

## String Syntax

A concise string syntax is provided for easy location specification:

**Format:** `<file_path>:<scope>@<find>`

**Scope formats:**
- `<line>` - Single line number (e.g., `42`)
- `<start>,<end>` - Line range with comma (e.g., `10,20`)
- `<start>-<end>` - Line range with dash (e.g., `10-20`)
- `<symbol_path>` - Symbol path with dots (e.g., `MyClass.my_method`)

**Examples:**
```python
# File with find pattern only
"foo.py@self.<|>"

# Line scope with find
"foo.py:42@return <|>result"

# Line range scope (comma or dash)
"foo.py:10,20@if <|>condition"
"foo.py:10-20@if <|>condition"

# Symbol scope with find
"foo.py:MyClass.my_method@self.<|>"

# Symbol scope only (for declaration position)
"foo.py:MyClass"
```
"foo.py:L10-20@if <|>condition"
```

## Position Resolution Rules

| Scope         | Find           | Resolution Result                            |
| ------------- | -------------- | -------------------------------------------- |
| `SymbolScope` | `None`         | Position of the symbol's declared name       |
| `SymbolScope` | With marker    | Marked position within the symbol body       |
| `SymbolScope` | Without marker | Start of matched text within the symbol body |
| `LineScope`   | `None`         | First non-whitespace character of the line   |
| `LineScope`   | With marker    | Marked position within the line              |
| `LineScope`   | Without marker | Start of matched text within the line        |
| `None`        | With marker    | Global search, marked position               |
| `None`        | Without marker | Global search, start of matched text         |
| `None`        | `None`         | ❌ Invalid, validation should failure         |

## Whitespace Handling

To balance flexibility and precision, the matching engine uses a **token-aware** whitespace strategy rather than exact string matching or full fuzzy matching.

### Tokenization Strategy

The search pattern is first tokenized into identifiers, operators, and explicit whitespace. The matching then follows these rules:

1. **Identifiers remain atomic**: Spaces are never allowed within an identifier (e.g., `int` will not match `i n t`).
2. **Flexible operator spacing**: Zero or more whitespace characters (`\s*`) are allowed between identifiers and operators, or between operators.
3. **Mandatory explicit whitespace**: If the search pattern contains explicit whitespace, the source must contain at least one whitespace character (`\s+`) at that position.

### Behavior Examples

| Input       | Matching Logic                           | Matches                   | Rejects   |
| ----------- | ---------------------------------------- | ------------------------- | --------- |
| `int a`     | Requires space between tokens            | `int a`, `int  a`         | `inta`    |
| `a+b`       | Allows flexible spacing around operators | `a+b`, `a + b`            | `ab`      |
| `foo.bar`   | Allows flexible spacing around dot       | `foo.bar`, `foo . bar`    | `foobar`  |
| `foo(x, y)` | Allows flexible spacing; preserves comma | `foo(x, y)`, `foo( x,y )` | `foo(xy)` |

### Empty Find Pattern

An empty `find` pattern (or whitespace-only) with a marker returns:
- Offset 0 if both before and after segments are empty.
- Otherwise, it is treated as a mandatory whitespace pattern (requiring at least one whitespace character).

### Design Rationale

#### Why Not Exact String Matching?
Code formatting varies across teams and tools. Exact matching would break on variations in indentation (spaces vs tabs), spacing around operators, or line continuation differences.

#### Why Not Full Fuzzy Matching?
Overly permissive matching creates ambiguity. For example, `int a` matching `inta` changes semantic meaning, and cross-line matches can accidentally hit unintended code structures.

#### Why Token-Based?
Token boundaries align with programming language semantics. It preserves identifier integrity while allowing natural operator spacing variations, matching the developer's mental model of "what should match".

## LSP Capability Mapping

### Capabilities Requiring Position

| LSP Capability               | Positioning Need            | Locate Usage                     |
| ---------------------------- | --------------------------- | -------------------------------- |
| `textDocument/definition`    | Identifier position         | `find="<\|>identifier"`          |
| `textDocument/references`    | Symbol declaration position | `SymbolScope(symbol_path=[...])` |
| `textDocument/rename`        | Symbol declaration position | `SymbolScope(symbol_path=[...])` |
| `textDocument/hover`         | Any identifier              | `find="<\| >target"`             |
| `textDocument/completion`    | Trigger point               | `find="obj.<\| >"`               |
| `textDocument/signatureHelp` | Inside parentheses          | `find="func(<\| >"`              |

### Capabilities Requiring Range

| LSP Capability            | Positioning Need    | LocateRange Usage                         |
| ------------------------- | ------------------- | ----------------------------------------- |
| `textDocument/codeAction` | Selected code range | `SymbolScope` or `find="selected text"`   |
| `textDocument/formatting` | Formatting range    | `SymbolScope` to select the entire symbol |

## Usage Examples

### 1. Find All References of a Symbol

```python
# Option 1: Using SymbolScope
Locate(
    file_path="models.py",
    scope=SymbolScope(symbol_path=["MyClass"])
)

# Option 2: Using find pattern
Locate(
    file_path="models.py",
    find="class <|>MyClass"
)

# Or using string syntax:
parse_locate_string("models.py@class <|>MyClass")
```

The resolver treats `SymbolScope` as the declaration position of the class name `MyClass` in the source code. Alternatively, using `find` with a pattern like `"class <|>MyClass"` locates the same position through text matching. Both approaches are suitable for `references`, `rename`, etc.

### 2. Get Hover Information for a Variable

```python
# Locate the 'result' variable within the 'process' function
Locate(
    file_path="utils.py",
    scope=SymbolScope(symbol_path=["process"]),
    find="return <|>result"
)

# Or using string syntax:
parse_locate_string("utils.py:process@return <|>result")
```

First narrows down to the `process` function body, then searches for `return result` within it, positioning at the start of `result`.

### 3. Trigger Code Completion

```python
# Locate the position after 'self.'
Locate(
    file_path="service.py",
    find="self.<|>"
)

# Or using string syntax:
parse_locate_string("service.py@self.<|>")
```

Global search for `self.`, positioning right after the dot to trigger member completion.

### 4. Get Code Actions

```python
# Select the entire function body
LocateRange(
    file_path="handlers.py",
    scope=SymbolScope(symbol_path=["handle_request"])
)

# Or using string syntax for SymbolScope:
parse_locate_string("handlers.py:handle_request")

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

### Q2: Why is the marker optional?

Often, locating at the start of the matched text is sufficient:

```python
# Locate the call site of deprecated_func
Locate(file_path="old.py", find="deprecated_func(")
```

Forcing a marker everywhere would increase the cognitive load on the Agent.

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

### Q5: Why automatic marker detection with nested brackets?

The automatic marker detection using nested brackets (`<|>`, `<<|>>`, etc.) provides:

1. **No configuration needed**: Agents don't need to specify a custom marker field
2. **Conflict resolution**: If the code contains `<|>`, agents can simply use `<<|>>`
3. **Clear hierarchy**: The nesting levels make it obvious which marker is intended
4. **Simple rule**: "Use the deepest unique marker" is easy to understand

```python
# When <|> appears in the source code
Locate(file_path="parser.py", find="token = <|> HERE <<|>> value")
# Automatically uses <<|>> as the position marker
```

### Q6: Why add string syntax?

The string syntax `<file_path>:<scope>@<find>` provides a concise format that:

1. **Reduces verbosity**: Agents can generate shorter location strings
2. **Human-readable**: Easy to read and understand at a glance
3. **Copy-paste friendly**: Can be easily shared in logs or documentation
4. **Optional but convenient**: The full object API is still available

```python
# Compact string format
"foo.py:MyClass.method@return <|>result"

# Equivalent to:
Locate(
    file_path="foo.py",
    scope=SymbolScope(symbol_path=["MyClass", "method"]),
    find="return <|>result"
)
```

### Q7: What if I need multiple markers in the same text?

The automatic marker detection supports up to 10 nesting levels. If you need to specify a position in text that contains multiple markers, use a deeper nesting level:

```python
# If your code contains both <|> and <<|>>
Locate(file_path="parser.py", find="a <|> b <<|>> c <<<|>>> d")
# Use <<<|>>> as the position marker
```

Only one marker should appear exactly once in the find text to be used as the position marker.

### Q8: Text matching rules in Find?

- Matching is **literal** (not regex), but with intelligent whitespace handling (see [Whitespace Handling](#whitespace-handling)).
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
