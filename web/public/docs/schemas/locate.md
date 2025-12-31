# Locate API

The Locate API provides a unified way to specify a position or range in the codebase. It is used as a base for many other requests like [`SymbolRequest`](symbol.md), [`ReferenceRequest`](reference.md), and [`CallHierarchyRequest`](call_hierarchy.md).

## Locate

The `Locate` model uses a two-stage approach: **scope** (optional) → **find** (optional, but at least one required).

### Resolution Rules

1. **SymbolScope without find**: Returns the symbol declaration position (for references, rename)
2. **With find containing marker**: Returns the marker position
3. **With find only**: Returns the start of matched text
4. **No scope + find**: Searches the entire file

### Locate Fields

| Field       | Type                                    | Default    | Description                                                      |
| :---------- | :-------------------------------------- | :--------- | :--------------------------------------------------------------- |
| `file_path` | `string`                                | Required   | Path to search in.                                               |
| `scope`     | `LineScope` \| `SymbolScope` \| `null`  | `null`     | Optional: narrow search to symbol body or line range.            |
| `find`      | `string` \| `null`                      | `null`     | Text pattern with marker for exact position.                     |
| `marker`    | `string`                                | `"<HERE>"` | Position marker in find pattern. Change if source contains `"<HERE>"`. |

### LineScope

| Field  | Type                              | Description                          |
| :----- | :-------------------------------- | :----------------------------------- |
| `line` | `number` \| `[number, number]`    | Line number or (start, end) range (1-based). |

### SymbolScope

| Field         | Type       | Description                                              |
| :------------ | :--------- | :------------------------------------------------------- |
| `symbol_path` | `string[]` | Symbol hierarchy, e.g., `["MyClass", "my_method"]`.      |

## LocateRange

For selecting a range of text instead of a point.

| Field       | Type                                    | Default    | Description                                       |
| :---------- | :-------------------------------------- | :--------- | :------------------------------------------------ |
| `file_path` | `string`                                | Required   | Path to search in.                                |
| `scope`     | `LineScope` \| `SymbolScope` \| `null`  | `null`     | Scope defines the range; if symbol, uses symbol's full range. |
| `find`      | `string` \| `null`                      | `null`     | Text to match; matched text becomes the range.     |

## LocateRequest

| Field    | Type      | Description                   |
| :------- | :-------- | :---------------------------- |
| `locate` | `Locate`  | The location to find.         |

## LocateRangeRequest

| Field    | Type         | Description                   |
| :------- | :----------- | :---------------------------- |
| `locate` | `LocateRange`| The range to locate.          |

## LocateResponse

| Field       | Type       | Description                                               |
| :---------- | :--------- | :-------------------------------------------------------- |
| `file_path` | `string`   | Resolved file path.                                       |
| `position`  | `Position` | The coordinates (line, character) of the match.           |

## Common Types

### Position

| Field       | Type     | Description                 |
| :---------- | :------- | :-------------------------- |
| `line`      | `number` | 1-based line number.        |
| `character` | `number` | 1-based character offset.   |

### Range

| Field   | Type       | Description                   |
| :------ | :--------- | :---------------------------- |
| `start` | `Position` | Start position (inclusive).   |
| `end`   | `Position` | End position (exclusive).     |

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

### Scenario 2: Completion trigger point (with marker)

```json
{
  "locate": {
    "file_path": "foo.py",
    "find": "self.<HERE>"
  }
}
```

### Scenario 3: Using custom marker (when source contains "<HERE>")

```json
{
  "locate": {
    "file_path": "foo.py",
    "find": "x = <|>value",
    "marker": "<|>"
  }
}
```

### Scenario 4: Finding a location within a specific symbol

```json
{
  "locate": {
    "file_path": "foo.py",
    "scope": {
      "symbol_path": ["process"]
    },
    "find": "return <HERE>result"
  }
}
```

#### Markdown Rendered for LLM

```markdown
Located `foo.py` at 42:10
```
