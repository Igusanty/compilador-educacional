"""Parse the scanner's tokens for the documented, line-oriented Python subset."""

import re
from itertools import groupby


COMPARISONS = {'==', '!=', '<', '<=', '>', '>='}


class SyntaxDiagnostic(Exception):
    def __init__(self, token, expected, context):
        found = token['lexema']
        super().__init__(f"Esperado {', '.join(expected)} {context}. Encontrado: {found}.")
        self.data = {
            'tipo': 'ERRO_SINTATICO', 'linha': token['linha'],
            'coluna': token['coluna'], 'encontrado': found,
            'esperado': expected, 'mensagem': str(self),
        }


def node(kind, first, last, children=(), **attributes):
    return {
        'tipo': kind, 'filhos': list(children),
        'inicio': first['inicio'], 'fim': last['fim'],
        'linha': first['linha'], 'coluna': first['coluna'],
        'linha_final': last.get('linha_final', last['linha']),
        'coluna_final': last.get('coluna_final', last['coluna'] + last['fim'] - last['inicio']),
        **attributes,
    }


class Line:
    def __init__(self, tokens, end):
        self.tokens = iter(tokens)
        self.end = end
        self.current = next(self.tokens, end)
        self.last = self.current

    def take(self):
        token = self.current
        self.last = token
        self.current = next(self.tokens, self.end)
        return token

    def expect(self, expected, context):
        if expected not in (self.current['lexema'], self.current['tipo']):
            raise SyntaxDiagnostic(self.current, [expected], context)
        return self.take()

    def binary(self, operand, operators):
        left = operand()
        while self.current['lexema'] in operators:
            operator = self.take()
            right = operand()
            left = node('OperacaoBinaria', left, right, [left, right], operador=operator['lexema'])
        return left

    def factor(self, depth):
        token = self.current
        if depth >= 24:
            raise SyntaxDiagnostic(token, ['expressão menos aninhada'], 'neste subconjunto')
        if token['lexema'] in {'+', '-'}:
            self.take()
            operand = self.factor(depth + 1)
            return node('OperacaoUnaria', token, operand, [operand], operador=token['lexema'])
        if token['lexema'] == '(':
            self.take()
            result = self.expression(depth + 1)
            end = self.expect(')', 'para fechar o grupo')
            return {**result, 'inicio': token['inicio'], 'linha': token['linha'],
                    'coluna': token['coluna'], 'fim': end['fim'], 'linha_final': end['linha'],
                    'coluna_final': end['coluna'] + 1}
        if token['tipo'] == 'IDENTIFICADOR':
            self.take()
            return node('Identificador', token, token, nome=token['lexema'])
        if token['tipo'] in {'LITERAL_INTEIRO', 'LITERAL_REAL'}:
            self.take()
            return node('Inteiro' if token['tipo'] == 'LITERAL_INTEIRO' else 'Real',
                        token, token, valor=token['lexema'])
        raise SyntaxDiagnostic(token, ['número', 'identificador', '('], 'como operando')

    def expression(self, depth=0):
        def product():
            return self.binary(lambda: self.factor(depth), {'*', '/'})

        def sum_at_depth():
            return self.binary(product, {'+', '-'})

        left = sum_at_depth()
        if self.current['lexema'] in COMPARISONS:
            operator = self.take()
            right = sum_at_depth()
            return node('Comparacao', left, right, [left, right], operador=operator['lexema'])
        return left


class Parser:
    def __init__(self, source, tokens):
        physical_lines = re.split(r'\r\n|\r|\n', source)
        self.lines = []
        for row, group in groupby(tokens, key=lambda token: token['linha']):
            line_tokens = list(group)
            first = line_tokens[0]
            prefix = physical_lines[row - 1][:first['coluna'] - 1]
            end = boundary('fim da linha', row, line_tokens[-1]['fim'],
                           line_tokens[-1]['coluna'] + len(line_tokens[-1]['lexema']))
            self.lines.append((len(prefix), '\t' in prefix, line_tokens, end))
        self.eof = boundary('fim do código', len(physical_lines), len(source), len(physical_lines[-1]) + 1)
        self.index = 0

    def first(self):
        if self.index < len(self.lines):
            return self.lines[self.index][2][0]
        return self.eof

    def block(self, indent, depth):
        if depth > 24:
            raise SyntaxDiagnostic(self.first(), ['menos blocos aninhados'], 'neste subconjunto')
        statements = []
        while self.index < len(self.lines):
            width, has_tab, tokens, end = self.lines[self.index]
            first = tokens[0]
            if width < indent or (width == indent and first['lexema'] == 'else' and statements):
                break
            if has_tab:
                raise SyntaxDiagnostic(first, ['indentação usando somente espaços'], 'no início do comando')
            if width != indent:
                expected = 'sem indentação' if indent == 0 else f'recuo de {indent} espaços'
                raise SyntaxDiagnostic(first, [f'comando {expected}'], 'neste bloco')
            if first['lexema'] == 'else':
                raise SyntaxDiagnostic(first, ['if correspondente'], 'antes deste else')
            if len(tokens) > 128:
                raise SyntaxDiagnostic(tokens[128], ['até 128 tokens por linha'], 'neste subconjunto')
            line = Line(tokens, end)
            self.index += 1
            if first['lexema'] == 'if':
                statements.append(self.conditional(line, indent, depth))
                continue
            name = line.expect('IDENTIFICADOR', 'para iniciar uma atribuição ou use if para um condicional')
            line.expect('=', 'depois do nome da variável')
            value = line.expression()
            line.expect('fim da linha', 'depois da expressão')
            target = node('Identificador', name, name, nome=name['lexema'])
            statements.append(node('Atribuicao', name, value, [target, value]))
        return statements

    def suite(self, parent_indent, depth):
        if self.index == len(self.lines) or self.lines[self.index][0] <= parent_indent:
            raise SyntaxDiagnostic(self.first(), ['comando indentado'], 'depois dos dois-pontos')
        indent = self.lines[self.index][0]
        statements = self.block(indent, depth + 1)
        return node('Bloco', statements[0], statements[-1], statements)

    def conditional(self, line, indent, depth):
        start = line.take()
        condition = line.expression()
        line.expect(':', 'depois da condição do if')
        line.expect('fim da linha', 'depois dos dois-pontos')
        children = [condition, self.suite(indent, depth)]
        if self.index < len(self.lines):
            width, has_tab, tokens, end = self.lines[self.index]
            if width == indent and tokens[0]['lexema'] == 'else':
                if has_tab:
                    raise SyntaxDiagnostic(tokens[0], [f'{indent} espaços de indentação'], 'antes de else')
                alternative = Line(tokens, end)
                alternative.take()
                alternative.expect(':', 'depois do else')
                alternative.expect('fim da linha', 'depois dos dois-pontos')
                self.index += 1
                children.append(self.suite(indent, depth))
        return node('Condicional', start, children[-1], children)

    def parse(self):
        statements = self.block(0, 0)
        if self.index < len(self.lines):
            raise SyntaxDiagnostic(self.first(), ['if correspondente'], 'antes deste else')
        if not statements:
            return node('Programa', self.eof, self.eof)
        return node('Programa', statements[0], statements[-1], statements)


def boundary(label, row, offset, column):
    return {'tipo': label, 'lexema': label, 'linha': row, 'coluna': column,
            'inicio': offset, 'fim': offset}


def analyze_syntax(source, tokens):
    try:
        ast = Parser(source, tokens).parse()
    except SyntaxDiagnostic as error:
        return {'sucesso': False, 'ast': None, 'erros': [error.data]}
    return {'sucesso': True, 'ast': ast, 'erros': []}
