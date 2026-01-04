# Test Relation API

The Test Relation API bridges the gap between production code and test code. It helps Agents perform targeted verification ("I changed X, what should I run?") and understand test failures ("Test Y failed, what does it cover?").

## TestRelationRequest

| Field       | Type                       | Default     | Description                                           |
| :---------- | :------------------------- | :---------- | :---------------------------------------------------- |
| `locate`    | [`Locate`](locate.md)      | Required    | The symbol to analyze (source function or test case). |
| `direction` | `"to_test" \| "to_source"` | `"to_test"` | Find tests for source, or find source for tests.      |

## TestRelationResponse

| Field           | Type                 | Description                                    |
| :-------------- | :------------------- | :--------------------------------------------- |
| `symbol`        | `SymbolInfo`         | The resolved input symbol.                     |
| `direction`     | `string`             | The direction used.                            |
| `related_items` | `TestRelationItem[]` | List of found related items (tests or source). |

### TestRelationItem

| Field       | Type     | Description                                                         |
| :---------- | :------- | :------------------------------------------------------------------ |
| `name`      | `string` | Name of the related item (e.g., `test_add`).                        |
| `kind`      | `string` | Symbol kind (e.g., `function`, `class`).                            |
| `file_path` | `string` | Path to the file.                                                   |
| `range`     | `Range`  | Location in the file.                                               |
| `strategy`  | `string` | How the relation was found: `reference`, `convention`, or `import`. |

## Implementation Guide

This API uses a multi-strategy approach to find relations, combining LSP capabilities with heuristic rules.

### Direction: `to_test` (Source -> Test)

1.  **LSP References (Strongest Signal)**:
    - Call `textDocument/references` on the source symbol.
    - Filter results: Keep files located in `tests/` directories or matching pattern `*test*`/`*spec*`.
    - Mark as `strategy: reference`.
2.  **Naming Convention (Heuristic)**:
    - Infer potential test names (e.g., `add` -> `test_add`, `TestAdd`).
    - Use `workspace/symbol` to search for these names.
    - Mark as `strategy: convention`.
3.  **Module Imports (Broadest Signal)**:
    - Identify which test files import the source module.
    - Mark as `strategy: import`.

### Direction: `to_source` (Test -> Source)

1.  **LSP Outgoing Calls (Strongest Signal)**:
    - Analyze the test function body.
    - Use `textDocument/definition` on symbols used within the test.
    - Filter results: Keep symbols defined in the project's source directory (exclude external libs).
    - Mark as `strategy: reference`.
2.  **Naming Convention (Heuristic)**:
    - Infer source name from test name (e.g., `test_add` -> `add`).
    - Use `workspace/symbol` to search.
    - Mark as `strategy: convention`.

## Example Usage

### Scenario 1: Finding tests for a modified function

#### Request

```json
{
  "locate": {
    "file_path": "src/calculator.py",
    "scope": {
      "symbol_path": ["add"]
    }
  },
  "direction": "to_test"
}
```

#### Markdown Rendered for LLM

```markdown
# Test Relation for `add` (to_test)

Found 2 related item(s):

- **test_add_basic** (`function`)
  - File: `tests/test_calculator.py`
  - Line: 15
  - Strategy: `convention`
- **test_add_edge_cases** (`function`)
  - File: `tests/test_calculator.py`
  - Line: 28
  - Strategy: `reference`
```

### Scenario 2: Finding source code for a failing test

#### Request

```json
{
  "locate": {
    "file_path": "tests/test_auth.py",
    "scope": {
      "symbol_path": ["TestLogin", "test_invalid_password"]
    }
  },
  "direction": "to_source"
}
```

#### Markdown Rendered for LLM

```markdown
# Test Relation for `test_invalid_password` (to_source)

Found 1 related item(s):

- **AuthService.login** (`method`)
  - File: `src/services/auth.py`
  - Line: 42
  - Strategy: `reference`
```

## Pending Issues

- **TBD**: Improving heuristic accuracy and supporting more language-specific test patterns (e.g., nested test classes).
