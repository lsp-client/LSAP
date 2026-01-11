# Locate API

The Locate API provides a unified way to specify a position or range in the codebase.
It is used as a base for many other requests like `SymbolRequest`, `ReferenceRequest`,
and `HierarchyRequest`.

## String Syntax

A concise string syntax is available: `<file_path>:<scope>@<find>`

### Scope formats

- `<line>`: Single line number (e.g., `"42"`)
- `<start>,<end>`: Line range with comma (e.g., `"10,20"`)
- `<start>-<end>`: Line range with dash (e.g., `"10-20"`)
- `<symbol_path>`: Symbol path with dots (e.g., `"MyClass.my_method"`)

### Examples

- `"foo.py@self.<|>"`
- `"foo.py:42@return <|>result"`
- `"foo.py:10,20@if <|>condition"`
- `"foo.py:MyClass.my_method@self.<|>"`
- `"foo.py:MyClass"`

## References

- [LineScope.json](./LineScope.json)
- [Locate.json](./Locate.json)
- [LocateRange.json](./LocateRange.json)
- [LocateRangeRequest.json](./LocateRangeRequest.json)
- [LocateRangeResponse.json](./LocateRangeResponse.json)
- [LocateRequest.json](./LocateRequest.json)
- [LocateResponse.json](./LocateResponse.json)
- [SymbolScope.json](./SymbolScope.json)
