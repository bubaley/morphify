from datetime import datetime

import pytest

from morphify import TemplateMorpher, ValueMorpher


def test_numeric_literal_passthrough():
    tpl = 'Value: {{ 123 }}'
    assert TemplateMorpher(tpl, {}).render() == 'Value: 123'


def test_if_invalid_args_exposes_error():
    # if requires exactly 3 args -> should expose ERROR marker, not crash
    tpl = '{{ if($x) }}'
    out = TemplateMorpher(tpl, {'x': True}).render()
    assert 'ERROR:' in out


def test_format_invalid_args_exposes_error():
    # format requires exactly 2 args -> should expose ERROR marker, not crash
    tpl = '{{ format($x) }}'
    out = TemplateMorpher(tpl, {'x': 1}).render()
    assert 'ERROR:' in out


def test_concat_with_function_and_commas_respects_paren_depth():
    # Ensures split_concat respects parentheses and quotes
    tpl = "{{ 'a' + format($date, 'DD,MM,YYYY') }}"
    rendered = TemplateMorpher(tpl, {'date': '2025-10-05'}).render()
    assert rendered == 'a05,10,2025'


def test_variable_path_edge_cases():
    class Obj:
        def __init__(self):
            self.attr = 'ok'

    ctx = {
        'arr': [1, 2],
        'obj': Obj(),
    }

    # Out-of-range index -> empty string
    assert TemplateMorpher('{{ $arr.5 }}', ctx).render() == ''
    # Non-digit segment on list -> empty string
    assert TemplateMorpher('{{ $arr.a }}', ctx).render() == ''
    # Attribute access success
    assert TemplateMorpher('{{ $obj.attr }}', ctx).render() == 'ok'
    # Attribute access failure -> empty string
    assert TemplateMorpher('{{ $obj.missing }}', ctx).render() == ''


def test_value_morpher_default_passthrough_when_no_match():
    # Unknown fmt falls back to str(value)
    assert ValueMorpher('???', 5).render() == '5'


def test_value_morpher_percentage_helper_direct_call():
    # Cover _percentage_format branch directly
    assert ValueMorpher._percentage_format('0.00%', 1.234) == '123.40%'


def test_value_morpher_date_from_datetime():
    dt = datetime(2025, 10, 5, 2, 40)
    assert ValueMorpher('DD/MM/YY HH:mm', dt).render() == '05/10/25 02:40'


def test_value_morpher_date_unsupported_type():
    with pytest.raises(ValueError):
        ValueMorpher('DD.MM.YYYY', object()).render()
