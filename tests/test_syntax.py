import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from scanner import scan
from syntax_analysis import analyze_syntax


def parse(source):
    lexical = scan(source)
    assert lexical['sucesso']
    return analyze_syntax(source, lexical['tokens'])


@pytest.mark.parametrize('expression,root,child,index', [
    ('2 + 3 * 4', '+', '*', 1),
    ('10 - 3 - 2', '-', '-', 0),
    ('(10 + 5) * 2', '*', '+', 0),
    ('-3.5 < +2', '<', '-', 0),
])
def test_expression_structure(expression, root, child, index):
    result = parse(f'x = {expression}')
    assignment = result['ast']['filhos'][0]
    target, value = assignment['filhos']
    assert target['nome'] == 'x'
    assert value['operador'] == root
    assert value['filhos'][index]['operador'] == child


def test_nested_blocks_positions_and_line_endings():
    source = 'if x:\r\n  if y:\r    x = 1\n  else:\n    x = 2\nelse:\n  x = 0'
    program = parse(source)['ast']
    condition = program['filhos'][0]
    _, then, otherwise = condition['filhos']
    nested = then['filhos'][0]
    assert len(nested['filhos']) == 3
    target = otherwise['filhos'][0]['filhos'][0]
    assert (target['linha'], target['coluna'], target['coluna_final']) == (7, 3, 4)
    assert source[target['inicio']:target['fim']] == 'x'
    assert program['fim'] == len(source)


@pytest.mark.parametrize('source,found,expected,row,col', [
    ('x = (1 + 2', 'fim da linha', ')', 1, 11),
    ('x =', 'fim da linha', 'número', 1, 4),
    ('x = 1 / * 2', '*', 'número', 1, 9),
    ('if x:', 'fim do código', 'comando indentado', 1, 6),
    ('if x:\ny = 2', 'y', 'comando indentado', 2, 1),
    ('else:\n  x = 2', 'else', 'if correspondente', 1, 1),
    ('  x = 1', 'x', 'comando sem indentação', 1, 3),
    ('if x:\n\tx = 2', 'x', 'indentação usando somente espaços', 2, 2),
    ('x = 1 < 2 < 3', '<', 'fim da linha', 1, 11),
])
def test_diagnostics(source, found, expected, row, col):
    result = parse(source)
    assert result['sucesso'] is False and result['ast'] is None
    error, = result['erros']
    assert error['encontrado'] == found and expected in error['esperado']
    assert (error['linha'], error['coluna']) == (row, col)


@pytest.mark.parametrize('source', ['', '# comentário\n\n'])
def test_empty_program(source):
    assert parse(source)['ast']['filhos'] == []


@pytest.mark.parametrize('source', [
    'x = ' + '(' * 30 + '1' + ')' * 30,
    'x = ' + '+'.join(['1'] * 100),
    ''.join(' ' * i + 'if x:\n' for i in range(26)) + ' ' * 26 + 'x = 1',
])
def test_complexity_limits_are_reported_as_diagnostics(source):
    assert parse(source)['sucesso'] is False
