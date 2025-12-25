# Liquid Cheatsheet

Based on [Shopify Liquid Documentation](https://shopify.github.io/liquid/).

## Basics

### Syntax

- Objects: `{{ variable }}` - Outputs the value of a variable.
- Tags: `{% logic %}` - Logic and control flow. No visible output.
- Filters: `{{ "hello" | upcase }}` - Modifies the output of an object.
- Comments:
  ```liquid
  {% comment %}
    This is a comment.
  {% endcomment %}
  ```

### Whitespace Control

Adding a hyphen to a tag or object (`{{-`, `-}}`, `{%-`, `-%}`) strips whitespace from that side.

```liquid
{%- assign name = "Liquid" -%}
Hello {{ name -}} !
```

### Truthy and Falsy

- Falsy: `nil` and `false`.
- Truthy: Everything else (including empty strings `""` and empty arrays `[]`).

### Operators

- `==`, `!=`, `>`, `<`, `>=`, `<=`, `or`, `and`
- `contains`: Checks for a substring in a string or an item in an array.

---

## Tags

### Control Flow

- if / elsif / else:
  ```liquid
  {% if product.title == "Shoes" %}
    It's shoes!
  {% elsif product.title == "Hat" %}
    It's a hat!
  {% else %}
    It's something else!
  {% endif %}
  ```
- unless: Opposite of `if`.
- case / when:
  ```liquid
  {% case handle %}
    {% when "cake" %} This is a cake.
    {% when "cookie" %} This is a cookie.
    {% else %} This is food.
  {% endcase %}
  ```

### Iteration

- for:
  ```liquid
  {% for product in collection.products %}
    {{ product.title }}
  {% else %}
    The collection is empty.
  {% endfor %}
  ```
- forloop object: `index` (1-based), `index0` (0-based), `first`, `last`, `length`.
- limit, offset, reversed:
  ```liquid
  {% for i in (1..10) limit:2 offset:3 reversed %} {{ i }} {% endfor %}
  ```
- cycle: `{% cycle "one", "two", "three" %}`
- tablerow: Generates an HTML table.

### Variable

- assign: `{% assign my_variable = "value" %}`
- capture:
  ```liquid
  {% capture my_variable %}
    Complex value with {{ other_var }}
  {% endcapture %}
  ```
- increment / decrement: `{% increment my_counter %}` (starts at 0, doesn't affect `assign` variables).

---

## Filters

### String

- `append`: `{{ "sales" | append: ".jpg" }}` → `sales.jpg`
- `capitalize`: `{{ "hello" | capitalize }}` → `Hello`
- `downcase` / `upcase`
- `replace` / `replace_first` / `remove` / `remove_first`
- `split`: `{{ "a~b" | split: "~" }}` → `["a", "b"]`
- `strip` / `lstrip` / `rstrip`: Remove whitespace.
- `truncate` / `truncatewords`: `{{ "long text" | truncate: 5 }}` → `lo...`
- `indent`: `{{ text | indent: 2 }}` - Indents each line by N spaces.
- `default`: `{{ var | default: "fallback" }}` - Returns fallback if var is nil or empty.
- `escape`: `{{ "<p>" | escape }}` → `&lt;p&gt;`

### Math

- `abs`, `at_least`, `at_most`, `ceil`, `floor`, `round`
- `plus`, `minus`, `times`, `divided_by`, `modulo`

### Array

- `first`, `last`, `index`: `{{ my_array[0] }}`
- `join`: `{{ my_array | join: ", " }}`
- `map`: Extracts a property from all items in an array.
- `reverse`, `sort`, `uniq`, `compact`
- `size`: Works on strings and arrays.
- `where`: Filters an array by a property value.
- `slice`: `{{ my_array | slice: 0, 2 }}` - Returns a subset of an array.

### Date

- `date`: `{{ "now" | date: "%Y-%m-%d" }}`
  - `%Y`: Year with century
  - `%m`: Month (01-12)
  - `%d`: Day of month (01-31)
  - `%H`: Hour (00-23)
  - `%M`: Minute (00-59)
  - `%S`: Second (00-59)
