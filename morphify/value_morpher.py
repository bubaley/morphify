from datetime import datetime
from typing import Any


class ValueMorpher:
    def __init__(self, fmt: str, value: Any):
        self.fmt = fmt
        self.value = value
        self.format_types = {
            'decimal': (
                lambda f: '.' in f and '0' in f,
                self._decimal_convert,
                self._decimal_format,
            ),
            'date': (
                lambda f: any(tok in f for tok in ['D', 'M', 'Y', 'H', 'm', 's']),
                self._date_convert,
                self._date_format,
            ),
        }

    def render(self) -> str:
        # Determine format type
        for matcher, converter, formatter in self.format_types.values():
            if matcher(self.fmt):
                # Convert value and format it
                converted_value = converter(self.value)
                return formatter(self.fmt, converted_value)
        return str(self.value)

    @staticmethod
    def _decimal_convert(val: Any) -> float:
        try:
            return float(val)
        except (ValueError, TypeError):
            raise ValueError(f"Cannot convert '{val}' to number")

    @staticmethod
    def _decimal_format(fmt: str, num: float) -> str:
        decimals = len(fmt.split('.')[1]) if '.' in fmt else 0
        return f'{num:.{decimals}f}'

    @staticmethod
    def _percentage_format(fmt: str, num: float) -> str:
        decimals = len(fmt.split('.')[1].replace('%', '')) if '.' in fmt else 0
        return f'{num * 100:.{decimals}f}%'

    @staticmethod
    def _date_convert(val: Any) -> datetime:
        if isinstance(val, datetime):
            return val
        if isinstance(val, (int, float)):
            return datetime.fromtimestamp(val)
        if isinstance(val, str):
            for f in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y'):
                try:
                    return datetime.strptime(val, f)
                except ValueError:
                    continue
            raise ValueError(f"Cannot convert '{val}' to date")
        raise ValueError(f"Cannot convert '{val}' to date")

    @staticmethod
    def _date_format(fmt: str, date_obj: datetime) -> str:
        mapping = {'DD': '%d', 'MM': '%m', 'YYYY': '%Y', 'YY': '%y', 'HH': '%H', 'mm': '%M', 'ss': '%S'}
        py_fmt = fmt
        for k, v in mapping.items():
            py_fmt = py_fmt.replace(k, v)
        return date_obj.strftime(py_fmt)
