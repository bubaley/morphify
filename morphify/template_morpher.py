import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from morphify.value_morpher import ValueMorpher


@dataclass(frozen=True)
class TemplateMorpherConfig:
    default_date_format: Optional[str] = None


class TemplateMorpher:
    def __init__(self, template: str, context: dict, config: Optional[TemplateMorpherConfig] = None):
        self.template = template
        self.context = context or {}
        self.config = config or TemplateMorpherConfig()

        # 🔹 Register all available template functions here
        self.functions = {
            'if': self._handle_if,
            'format': self._handle_format,
            # Easy to extend:
            # 'upper': self._handle_upper,
            # 'lower': self._handle_lower,
        }

    def render(self) -> str:
        """Main entry point — replaces {{...}} expressions with evaluated values."""

        def replacer(match):
            expr = match.group(1).strip()
            try:
                return str(self._eval_expr(expr, self.context))
            except Exception as e:
                # On error, keep it visible for debugging
                return f'{{{{ERROR: {e}}}}}'

        return re.sub(r'{{(.*?)}}', replacer, self.template)

    # -------------------------------------------------------
    # 🔹 Core expression evaluator
    # -------------------------------------------------------
    def _eval_expr(self, expr: str, context: dict):
        expr = expr.strip()

        # --- Check if expression starts with a registered function ---
        for func_name, func_handler in self.functions.items():
            if expr.startswith(f'{func_name}(') and expr.endswith(')'):
                return func_handler(expr, context)

        # --- Handle string concatenation (+) ---
        if '+' in expr:
            parts = self._split_concat(expr)
            return ''.join(str(self._eval_expr(p, context)) for p in parts)

        # --- String literal ---
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]

        # --- Variable reference ---
        if expr.startswith('$'):
            var_path = expr[1:]
            value = self._resolve_variable_path(context, var_path)
            return self._maybe_auto_format(value)

        # --- Fallback: return as-is (could be a number, etc.) ---
        return expr

    # -------------------------------------------------------
    # 🔹 Function handlers
    # -------------------------------------------------------
    def _handle_if(self, expr: str, context: dict):
        """Handles if(condition, then, else)"""
        inner = expr[len('if(') : -1]
        args = self._split_args(inner)
        if len(args) != 3:
            raise ValueError('if() requires exactly 3 arguments')
        condition = self._eval_expr(args[0], context)
        return self._eval_expr(args[1], context) if condition else self._eval_expr(args[2], context)

    def _handle_format(self, expr: str, context: dict):
        """Handles format(value, pattern)"""
        inner = expr[len('format(') : -1]
        args = self._split_args(inner)
        if len(args) != 2:
            raise ValueError('format() requires exactly 2 arguments')
        value = self._eval_expr(args[0], context)
        pattern_raw = args[1].strip()
        # Enforce quoting for pattern to avoid ambiguous parsing
        if not (
            (pattern_raw.startswith("'") and pattern_raw.endswith("'"))
            or (pattern_raw.startswith('"') and pattern_raw.endswith('"'))
        ):
            # Keep error style consistent with ValueFormatter passthrough
            return "value|format pattern must be quoted, e.g. 'DD.MM.YYYY'"
        fmt = pattern_raw.strip('"\'')
        try:
            return ValueMorpher(fmt, value).render()
        except Exception as e:
            return str(f'value|{e}')

    # -------------------------------------------------------
    # 🔹 Utility helpers
    # -------------------------------------------------------
    def _split_args(self, s: str):
        """Splits arguments by commas, respecting parentheses and quotes."""
        args, current, depth, in_quotes = [], '', 0, False
        for c in s:
            if c in ('"', "'"):
                in_quotes = not in_quotes
            elif c == '(' and not in_quotes:
                depth += 1
            elif c == ')' and not in_quotes:
                depth -= 1
            elif c == ',' and depth == 0 and not in_quotes:
                args.append(current.strip())
                current = ''
                continue
            current += c
        if current:
            args.append(current.strip())
        return args

    def _split_concat(self, s: str):
        """Splits by '+' respecting parentheses and quotes."""
        parts, current, depth, in_quotes = [], '', 0, False
        for c in s:
            if c in ('"', "'"):
                in_quotes = not in_quotes
            elif c == '(' and not in_quotes:
                depth += 1
            elif c == ')' and not in_quotes:
                depth -= 1
            elif c == '+' and depth == 0 and not in_quotes:
                parts.append(current.strip())
                current = ''
                continue
            current += c
        if current:
            parts.append(current.strip())
        return parts

    def _resolve_variable_path(self, context: dict, var_path: str):
        """Resolves dot-notated variable paths like 'user.address.city'.

        Supports dict keys and list/tuple indexes. On any missing step,
        returns empty string to keep rendering graceful.
        """
        current = context
        for segment in var_path.split('.'):
            if isinstance(current, dict):
                if segment in current:
                    current = current[segment]
                else:
                    return ''
            elif isinstance(current, (list, tuple)):
                if segment.isdigit():
                    idx = int(segment)
                    if 0 <= idx < len(current):
                        current = current[idx]
                    else:
                        return ''
                else:
                    return ''
            else:
                # Fallback: try attribute access, else fail gracefully
                try:
                    current = getattr(current, segment)
                except Exception:
                    return ''
        return current

    # -------------------------------------------------------
    # 🔹 Auto-format helpers
    # -------------------------------------------------------
    def _maybe_auto_format(self, value):
        """Applies default_date_format to date-like values when no explicit format() is used.

        If conversion fails or config is not set, returns the value as-is.
        """
        if isinstance(value, (date, datetime)) and self.config.default_date_format:
            return ValueMorpher._date_format(self.config.default_date_format, value)
        return value
