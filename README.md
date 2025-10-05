Morphium
========

Lightweight string templating with safe variable resolution and value formatting.

Key features
------------
- Simple `{{ ... }}` expressions with function calls and string concatenation
- Safe variable lookup with dot-paths (returns empty string on missing keys)
- Built-in helpers: `if(condition, then, else)` and `format(value, pattern)`
- Value formatting for decimals and dates with human-friendly patterns

Installation
------------

```bash
pip install morphium
```

Quick start
-----------

```python
from morphium import TemplateMorpher

tpl = "Hello, {{ if($name, $name, 'guest') }}! Today is {{ format($date, 'DD.MM.YYYY') }}."
print(TemplateMorpher(tpl, {"name": "Alex", "date": "2025-10-05"}).render())
# -> Hello, Alex! Today is 05.10.2025.
```

API
---

```python
from morphium import TemplateMorpher, ValueMorpher
```

- TemplateMorpher(template: str, context: dict, config: TemplateConfig | None = None).render() -> str
  - Replaces `{{ ... }}` expressions within `template` using values from `context`.
  - Supported features:
    - Variables: `$user.name`
    - Literals: `'text'`, "text"
    - Concatenation: `'A' + 'B' + $x`
    - Functions:
      - `if(condition, then, else)`
      - `format(value, pattern)` — pattern must be quoted

- ValueMorpher(fmt: str, value: Any).render() -> str
  - Automatically detects format type:
    - Decimal: patterns like `0.00` (precision is taken from the pattern)
    - Date: tokens like `DD`, `MM`, `YYYY`, `HH`, `mm`, `ss`

Configuration
-------------

```python
from morphium import TemplateMorpher
from morphium.morphium.template_morpher import TemplateConfig

tpl = 'Today: {{$date}}'  # no explicit format()
cfg = TemplateConfig(default_date_format='DD/MM/YY')
print(TemplateMorpher(tpl, {"date": "2025-10-05"}, config=cfg).render())
# -> Today: 05/10/25
```

Formatting examples
-------------------

```python
from morphium import ValueMorpher

ValueMorpher('0.000', '3.14159').render()  # '3.142'
ValueMorpher('DD/MM/YY HH:mm', 1728096000).render()  # timestamp -> '05/10/25 00:00'
```

Testing
-------

```bash
pytest -q
```

Coverage
--------

The project uses `coverage.py`. Settings live in `pyproject.toml`.

- Run locally:

```bash
coverage run -m pytest -q && coverage report
```

CI integrates with Codecov. Provide `CODECOV_TOKEN` if required.

Contributing
------------
- Run linters and tests before pushing:

```bash
uv sync --dev --locked
uv run pre-commit run --all-files
uv run pytest -q
```

License
-------
MIT
