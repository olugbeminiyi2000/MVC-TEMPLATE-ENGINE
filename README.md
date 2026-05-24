# v1 Template Engine

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![regex](https://img.shields.io/badge/regex-PyPI-orange?style=flat&logo=pypi&logoColor=white)

A lightweight template engine built in Python from scratch — no framework, no abstract syntax tree. It uses a linear state machine over a flat component list, indentation-based scope tracking, and a custom linked-list iterator to render variables, conditional blocks, and loops from plain text templates.

---

## Features

- **Variable substitution** — `{{ variable_name }}`
- **Conditional blocks** — `{% IF %}`, `{% ELIF %}`, `{% ELSE %}`, `{% ENDIF %}` with unlimited nesting
- **Boolean logic** — `NOT`, `AND`, `OR` operators in conditions
- **Loop blocks** — `{% FOR item IN iterable %}` / `{% ENDFOR %}` with support for nested loops
- **All Python iterables** — `list`, `tuple`, `set`, `dict`, `str`
- **Five custom exceptions** for precise error reporting

---

## Dependency

This project requires one third-party package:

| Package | Why it is needed |
|---------|-----------------|
| [`regex`](https://pypi.org/project/regex/) | Variable-width lookbehind assertions used to extract logic operators and loop variables from patterns — Python's built-in `re` module does not support these. |

### Setup

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate it
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Install the dependency
pip install -r requirements.txt
```

---

## Quick Start

Edit `template.txt` with your template content and `context_data` inside `engine/main_engine.py`, then run:

```bash
python -m engine.main_engine
```

To call the engine from another file:

```python
from engine.main_engine import run_template_engine

context_data = {
    "username": "Emmanuel",
    "items": [1, 2, 3],
    "show_details": True,
}

run_template_engine("template.txt", context_data)
```

> **Note:** `run_template_engine` prints the rendered output directly. The template filename is resolved relative to the project root.

---

## Template Syntax

### Variables

```
{{ variable_name }}
```

Substitutes the value of `variable_name` from `context_data` or the current loop scope.  
Whitespace around the name is flexible: `{{ name }}`, `{{name}}`, and `{{  name  }}` are all valid.  
If the resolved value is `None`, an empty string is rendered.

Variable names must be valid Python identifiers: start with a letter or `_`, followed by letters, digits, or underscores.

---

### Conditional Blocks

```
{% IF condition %}
    ...
{% ELIF other_condition %}
    ...
{% ELSE %}
    ...
{% ENDIF %}
```

- `{% ELIF %}` and `{% ELSE %}` are optional.
- Multiple `{% ELIF %}` branches are supported.
- Once one branch evaluates to true, all remaining `{% ELIF %}` and `{% ELSE %}` branches are skipped.
- Truthiness follows Python rules: `0`, `""`, `[]`, `{}`, `None`, and `False` are all falsy.
- Keywords must be **uppercase**: `IF`, `ELIF`, `ELSE`, `ENDIF`.

**Simple condition:**

```
{% IF is_active %}
    Account is active.
{% ENDIF %}
```

**With logic operators:**

```
{% IF NOT is_guest AND is_verified %}
    Full access granted.
{% ELIF is_admin OR is_superuser %}
    Admin access.
{% ELSE %}
    Access denied.
{% ENDIF %}
```

---

### Logic Operators

Supported inside `{% IF %}` and `{% ELIF %}` conditions only.

| Operator | Meaning |
|----------|---------|
| `NOT` | Negates the truthiness of the variable that immediately follows it |
| `AND` | True only when both sides are truthy |
| `OR`  | True when either side is truthy |

**Evaluation order: `NOT` first, then `AND`, then `OR`.**

```
{% IF NOT is_banned AND is_active OR is_admin %}
```

Evaluates as: `(NOT is_banned AND is_active) OR is_admin`

---

### Loop Blocks

```
{% FOR item IN collection %}
    {{ item }}
{% ENDFOR %}
```

- `item` is available as a variable inside the loop body.
- `collection` must be a key in `context_data` whose value is a `list`, `tuple`, `set`, `dict`, or `str`.
- If `collection` is a `dict`, iterating yields its **keys**.
- If `collection` is a `str`, iterating yields individual **characters**.
- A loop variable that is itself iterable can be used as the iterable in a nested loop.
- Keywords must be **uppercase**: `FOR`, `IN`, `ENDFOR`.

**Nested loop with condition:**

```
{% FOR group IN groups %}
    {% IF group %}
        {% FOR num IN group %}
            Number: {{ num }}
        {% ENDFOR %}
    {% ELSE %}
        Empty group.
    {% ENDIF %}
{% ENDFOR %}
```

---

## Indentation Rules

All block tags must be placed at a column that is a **multiple of 4 spaces** (0, 4, 8, 12, …).

```
{% IF condition %}              ← column 0  (0 × 4)
    content
    {% FOR item IN items %}     ← column 4  (1 × 4)
        {{ item }}
    {% ENDFOR %}                ← column 4  (1 × 4)
{% ENDIF %}                     ← column 0  (0 × 4)
```

A `PlacementError` is raised if any block tag is not at a valid column.

---

## Supported Iterable Types

| Type | Iteration behaviour |
|------|---------------------|
| `list` | In order |
| `tuple` | In order |
| `dict` | Keys only, in insertion order |
| `set` | Arbitrary order |
| `str` | Character by character |

---

## Error Reference

| Exception | When it is raised |
|-----------|-------------------|
| `VariableError` | A variable used in the template is not found in `context_data` or the current loop scope |
| `ConditionError` | An `{% IF %}` or `{% ELIF %}` block is not written correctly |
| `LoopError` | A `{% FOR %}` or `{% ENDFOR %}` block is not written correctly |
| `StructureError` | An `{% IF %}` block has no matching `{% ENDIF %}`, or a `{% FOR %}` has no matching `{% ENDFOR %}` |
| `PlacementError` | A block tag is not at a column that is a multiple of 4 spaces |

---

## Rendering Pipeline

Every call to `run_template_engine()` passes through eight stages in order:

```
1. Load             Read the template file from disk
2. Pattern Match    Find all {{ }}, {% IF %}, {% FOR %}, etc. using compiled regex
3. Error Check      Validate each matched pattern is correctly written
4. Structure Check  Verify every IF has an ENDIF, every FOR has an ENDFOR
5. Parse            Split the template into a flat list of (static_text, match) components
6. Validate         Confirm every variable and iterable exists in context_data or loop scope
7. Iterable Manager Convert all top-level iterables into linked lists for traversal
8. Render           Walk the component list, evaluate conditions, iterate loops, substitute variables
```

---

## Project Structure

```
template_engine/
│
├── engine/
│   ├── main_engine.py        Entry point — runs the full 8-stage pipeline
│   ├── file_loader.py        Reads the template file from disk
│   ├── pattern_matcher.py    Compiles and applies all regex patterns
│   ├── error_checker.py      Validates that each matched pattern is correctly written
│   ├── structure_checker.py  Validates IF/FOR block nesting and closure
│   ├── parser.py             Splits the template into a flat component list
│   ├── validator.py          Checks all variables and iterables exist
│   ├── iterable_manager.py   Converts top-level iterables to linked lists
│   └── renderer.py           Core rendering loop — conditions, loops, substitution
│
├── engine_core/
│   ├── patterns.py                    All compiled regex patterns
│   ├── exceptions.py                  Custom exception classes
│   ├── logic_nodes.py                 NOT, AND, OR linked-list nodes
│   ├── logic_condition.py             Builds the logic operator evaluation chain
│   ├── condition_truthy_falsy.py      Evaluates boolean conditions
│   ├── iterable_linkedlist.py         Linked-list node for iterable traversal
│   ├── create_iterable_linkedlist.py  Builds iterable linked lists from Python values
│   ├── iterable_utils.py              Validates iterable types and creates linked lists
│   └── placeholder_validation.py     Checks variable existence during validation stage
│
└── template.txt    Example template
```
