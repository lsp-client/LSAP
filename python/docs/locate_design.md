# Locate Capability Design

## Overview

The `locate` module provides a flexible text-based navigation system for locating specific positions or ranges within source files. It serves as a bridge between high-level semantic descriptions (e.g., "find variable `x` in function `foo`") and precise LSP positions.

Unlike traditional search that returns all matches, `locate` returns the **first match** within a specified scope, enabling deterministic navigation for code manipulation and analysis tasks.

## Core Components

### 1. Scope Mechanism

Scopes define the search boundary within a file:

- **`None` (Global Scope)**: Search the entire file
- **`LineScope`**: Search specific line(s)
  - Single line: `{"line": 10}`
  - Line range: `{"line": [10, 20]}`
- **`SymbolScope`**: Search within a symbol's range
  - Uses document symbols from LSP
  - Example: `{"symbol_path": ["MyClass", "my_method"]}`

The scope is resolved **before** pattern matching, establishing a well-defined search region.

### 2. Find Pattern Matching

The `find` parameter accepts a literal string that is converted to a regular expression with intelligent whitespace handling. This enables flexible matching while avoiding false positives.

**Key Design Decision**: Whitespace in source code varies due to formatting preferences, but token boundaries must remain intact.

### 3. Marker-Based Positioning

When `find` contains a marker (default: `<|>`), it splits the pattern into before/after segments:

```python
find = "int x <|> = 0"
# Matches: "int x = 0", "int x  = 0", "int x=0", etc.
# Returns position at the marker location (after "x")
```

Without a marker, the position points to the **start** of the match.

## Regex Whitespace Handling

### Token-Aware Matching Strategy

The `_to_regex` implementation uses **token-aware** whitespace handling to balance flexibility and precision:

```python
def _to_regex(text: str) -> str:
    """Convert search text to regex with sensible whitespace handling.

    - Explicit whitespace: matches one or more whitespace (\\s+)
    - Identifier-operator boundaries: matches zero or more whitespace (\\s*)
    - Within tokens: literal match (no flexibility)
    """
    tokens = re.findall(r"\w+|[^\w\s]+|\s+", text)
    if not tokens:
        return ""

    result: list[str] = []
    for i, token in enumerate(tokens):
        if token[0].isspace():
            result.append(r"\s+")
        else:
            result.append(re.escape(token))
            if i < len(tokens) - 1 and not tokens[i + 1][0].isspace():
                result.append(r"\s*")
    return "".join(result)
```

**Tokenization Strategy**:

1. Split input into: identifiers (`\w+`), operators (`[^\w\s]+`), whitespace (`\s+`)
2. Preserve tokens as atomic units
3. Insert `\s*` only at token boundaries (when no explicit whitespace exists)
4. Convert explicit whitespace to `\s+` (requires at least one space)

### Behavior Examples

| Input       | Generated Regex             | Matches                   | Rejects   |
| ----------- | --------------------------- | ------------------------- | --------- |
| `int a`     | `int\s+a`                   | `int a`, `int  a`         | `inta`    |
| `a+b`       | `a\s*\+\s*b`                | `a+b`, `a + b`            | `ab`      |
| `foo.bar`   | `foo\s*\.\s*bar`            | `foo.bar`, `foo . bar`    | `foobar`  |
| `foo(x, y)` | `foo\s*\(\s*x\s*,\s+y\s*\)` | `foo(x, y)`, `foo( x,y )` | `foo(xy)` |

**Key Properties**:

- Identifiers remain intact: `int` never matches `i n t`
- Operators allow flexible spacing: `a+b` ↔ `a + b`
- Explicit spaces are preserved: `int a` requires space between tokens

## Implementation Flow

### LocateCapability (Position)

1. **Read Document**: Load file content via LSP client
2. **Resolve Scope**: Convert scope specification to LSP range
3. **Pattern Matching**:
   - If `find` contains marker: split pattern, match, return marker position
   - If `find` without marker: match, return match start
   - If no `find`: return scope start (symbol selection or first non-whitespace)
4. **Convert to LSAP Position**: Return standardized position

### LocateRangeCapability (Range)

Similar flow, but returns the **range** of the matched pattern instead of a single position.

## Design Rationale

### Why Not Exact String Matching?

Code formatting varies across teams and tools. Exact matching would break on:

- Space vs tab indentation
- Single vs multiple spaces around operators
- Line continuation differences

### Why Not Full Fuzzy Matching?

Overly permissive matching creates ambiguity:

- `int a` matching `inta` changes semantic meaning
- Cross-line matches can match unintended code structures

### Why Token-Based?

Token boundaries align with programming language semantics:

- Preserves identifier integrity
- Allows natural operator spacing variations
- Matches developer mental model of "what should match"

## Edge Cases & Considerations

### Empty Find Pattern

An empty `find` pattern (or whitespace-only) with a marker returns:

- Offset 0 if both before/after are empty
- Otherwise treated as `\s+` pattern

### Symbol Scope Fallback

If a symbol path is not found, raises `NotFoundError` rather than falling back to global scope, ensuring deterministic behavior.

### First Match Only

Always returns the **first** match in document order. This design choice supports:

- Deterministic navigation for automation
- Predictable behavior for code generation
- Simpler error handling (found or not found)

## Future Enhancements

Potential areas for extension:

- **Multi-language awareness**: Language-specific tokenization for better accuracy
- **Semantic scopes**: Integration with LSP semantic tokens
- **Match disambiguation**: Options for nth-match or all-matches mode
- **Pattern escaping**: Explicit syntax to disable whitespace flexibility
