# Locate API

The Locate API provides a unified way to specify a position or range in the codebase. It is used as a base for many other requests like [`SymbolRequest`](symbol.md), [`ReferenceRequest`](reference.md), and [`HierarchyRequest`](draft/hierarchy.md).

## Locate

The `Locate` model uses a two-stage approach: **scope** (optional) → **find** (optional, but at least one required).

### Resolution Rules

1. **SymbolScope without find**: Returns the symbol declaration position (for references, rename)
2. **With find containing marker**: Returns the marker position (auto-detected using nested brackets)
3. **With find only**: Returns the start of matched text
4. **No scope + find**: Searches the entire file

### Automatic Marker Detection

Markers are automatically detected using nested bracket notation:
- `<|>` - Single level (default)
- `<<|>>` - Double level (if `<|>` appears multiple times)
- `<<<|>>>` - Triple level (if `<<|>>` appears multiple times)
- ... up to 10 nesting levels

The system automatically selects the marker with the deepest nesting level that appears exactly once in the find text.

### String Syntax

A concise string syntax is available: `<file_path>:<scope>@<find>`

**Scope formats:**
- `<line>` - Single line number (e.g., `42`)
- `<start>,<end>` - Line range with comma (e.g., `10,20`)
- `<start>-<end>` - Line range with dash (e.g., `10-20`)
- `<symbol_path>` - Symbol path with dots (e.g., `MyClass.my_method`)

**Examples:**
```
foo.py@self.<|>
foo.py:42@return <|>result
foo.py:10,20@if <|>condition
foo.py:MyClass.my_method@self.<|>
foo.py:MyClass
```

### Locate Fields

| Field       | Type                                   | Default  | Description                                           |
| :---------- | :------------------------------------- | :------- | :---------------------------------------------------- |
| `file_path` | `string`                               | Required | Path to search in.                                    |
| `scope`     | `LineScope` \| `SymbolScope` \| `null` | `null`   | Optional: narrow search to symbol body or line range. |
| `find`      | `string` \| `null`                     | `null`   | Text pattern with auto-detected marker.               |

### LineScope

| Field  | Type                           | Description                                  |
| :----- | :----------------------------- | :------------------------------------------- |
| `line` | `number` \| `[number, number]` | Line number or (start, end) range (1-based). |

### SymbolScope

| Field         | Type       | Description                                         |
| :------------ | :--------- | :-------------------------------------------------- |
| `symbol_path` | `string[]` | Symbol hierarchy, e.g., `["MyClass", "my_method"]`. |

## LocateRange

For selecting a range of text instead of a point.

| Field       | Type                                   | Default  | Description                                                   |
| :---------- | :------------------------------------- | :------- | :------------------------------------------------------------ |
| `file_path` | `string`                               | Required | Path to search in.                                            |
| `scope`     | `LineScope` \| `SymbolScope` \| `null` | `null`   | Scope defines the range; if symbol, uses symbol's full range. |
| `find`      | `string` \| `null`                     | `null`   | Text to match; matched text becomes the range.                |

## LocateRequest

| Field    | Type     | Description           |
| :------- | :------- | :-------------------- |
| `locate` | `Locate` | The location to find. |

## LocateRangeRequest

| Field    | Type          | Description          |
| :------- | :------------ | :------------------- |
| `locate` | `LocateRange` | The range to locate. |

## LocateResponse

| Field       | Type       | Description                                     |
| :---------- | :--------- | :---------------------------------------------- |
| `file_path` | `string`   | Resolved file path.                             |
| `position`  | `Position` | The coordinates (line, character) of the match. |

## Common Types

### Position

| Field       | Type     | Description               |
| :---------- | :------- | :------------------------ |
| `line`      | `number` | 1-based line number.      |
| `character` | `number` | 1-based character offset. |

### Range

| Field   | Type       | Description                 |
| :------ | :--------- | :-------------------------- |
| `start` | `Position` | Start position (inclusive). |
| `end`   | `Position` | End position (exclusive).   |

## Example Usage

### Scenario 1: Finding a symbol declaration

```json
{
  "locate": {
    "file_path": "foo.py",
    "scope": {
      "symbol_path": ["MyClass"]
    }
  }
}
```

Or using string syntax:
```
"foo.py:MyClass"
```

### Scenario 2: Completion trigger point (with marker)

```json
{
  "locate": {
    "file_path": "foo.py",
    "find": "self.<|>"
  }
}
```

Or using string syntax:
```
"foo.py@self.<|>"
```

### Scenario 3: Nested marker when <|> exists in source

```json
{
  "locate": {
    "file_path": "foo.py",
    "find": "x = <|> + y <<|>> z"
  }
}
```

The system automatically detects `<<|>>` as the unique position marker.

Or using string syntax:
```
"foo.py@x = <|> + y <<|>> z"
```

### Scenario 4: Finding a location within a specific symbol

```json
{
  "locate": {
    "file_path": "foo.py",
    "scope": {
      "symbol_path": ["process"]
    },
    "find": "return <|>result"
  }
}
```

Or using string syntax:
```
"foo.py:process@return <|>result"
```

#### Markdown Rendered for LLM

```markdown
Located `foo.py` at 42:10
```
