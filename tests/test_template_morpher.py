from datetime import date

from morphify import TemplateMorpher, TemplateMorpherConfig


def test_if_branching_and_vars():
    tpl = "Hello, {{ if($name, $name, 'guest') }}!"
    assert TemplateMorpher(tpl, {'name': 'Alex'}).render() == 'Hello, Alex!'
    assert TemplateMorpher(tpl, {}).render() == 'Hello, guest!'


def test_concat_and_literals():
    tpl = "A={{ 'x' + 'y' + 'z' }}"
    assert TemplateMorpher(tpl, {}).render() == 'A=xyz'


def test_nested_calls_and_format():
    tpl = "Date: {{ format($date, 'DD.MM.YYYY') }}"
    assert TemplateMorpher(tpl, {'date': '2025-10-05'}).render() == 'Date: 05.10.2025'


def test_nested_objects():
    tpl = '{{$document.number}}'
    assert TemplateMorpher(tpl, {'document': {'number': 1}}).render() == '1'


def test_auto_date_format_via_config():
    # No explicit format() call, date should be auto-formatted using config
    tpl = 'Today: {{$date}}'
    cfg = TemplateMorpherConfig(default_date_format='DD/MM/YY')
    out = TemplateMorpher(tpl, {'date': date(2025, 10, 5)}, config=cfg).render()
    assert out == 'Today: 05/10/25'


def test_error_format_without_qoute():
    tpl = 'Date: {{ format($date, DD.MM.YYYY) }}'
    out = TemplateMorpher(tpl, {'date': '2025-10-05'}).render()
    assert 'value|' in out  # error


def test_error_visibility():
    tpl = "{{ format('not-a-date', 'DD.MM.YYYY') }}"
    out = TemplateMorpher(tpl, {}).render()
    assert 'value|' in out  # error string passthrough from ValueFormatter
