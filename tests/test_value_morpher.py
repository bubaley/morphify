from datetime import datetime

import pytest

from morphium import ValueMorpher


def test_decimal_basic_rounding():
    assert ValueMorpher('0.', 123.4567).render() == '123'
    assert ValueMorpher('0.000', '3.14159').render() == '3.142'


def test_decimal_invalid():
    with pytest.raises(ValueError):
        ValueMorpher('0.00', 'abc').render()


def test_date_from_string():
    assert ValueMorpher('DD.MM.YYYY', '2025-10-05').render() == '05.10.2025'


def test_date_from_timestamp():
    ts = datetime(2025, 10, 5, 2, 40).timestamp()
    assert ValueMorpher('DD/MM/YY HH:mm', ts).render() == '05/10/25 02:40'
