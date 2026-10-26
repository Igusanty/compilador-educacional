"""Scanner manual para o subconjunto didático; não executa nem faz parsing."""
import re
KEYWORDS = {'if', 'else'}
OPERATORS = {'+', '-', '*', '/', '=', '==', '!=', '<', '>', '<=', '>='}
DELIMITERS = {'(', ')', ':'}

def scan(source):
    tokens, errors = [], []
    i, line, column = 0, 1, 1
    def emit(kind, text, start, row, col):
        tokens.append(dict(tipo=kind, lexema=text, linha=row, coluna=col, inicio=start, fim=start+len(text)))
    def fail(text, row, col, message):
        errors.append(dict(tipo='ERRO_LEXICO', lexema=text, linha=row, coluna=col, mensagem=message))
    while i < len(source):
        start, row, col = i, line, column
        c = source[i]
        if c in '\r\n':
            i += 2 if source[i:i+2] == '\r\n' else 1
            line += 1; column = 1
            continue
        if c in ' \t':
            i += 1; column += 1; continue
        if c == '#':
            while i < len(source) and source[i] not in '\r\n': i += 1
            column += i-start; continue
        if c.isascii() and (c.isalpha() or c == '_'):
            i += 1
            while i < len(source) and source[i].isascii() and (source[i].isalnum() or source[i]=='_'): i += 1
            text=source[start:i]
            emit('PALAVRA_RESERVADA' if text in KEYWORDS else 'IDENTIFICADOR',text,start,row,col)
        elif c.isascii() and c.isdigit():
            i += 1
            while i < len(source) and (source[i].isalnum() or source[i] in '._'): i += 1
            text=source[start:i]
            if re.fullmatch(r'(0|[1-9][0-9]*)',text): emit('LITERAL_INTEIRO',text,start,row,col)
            elif re.fullmatch(r'[0-9]+\.[0-9]+',text): emit('LITERAL_REAL',text,start,row,col)
            else: fail(text,row,col,'Literal inválido. Use inteiro decimal sem zeros iniciais ou real como 3.14; não junte letras ao número.')
        elif c in "\"'":
            quote=c; i+=1; closed=False
            while i < len(source) and source[i] not in '\r\n':
                if source[i] == '\\' and i+1 < len(source) and source[i+1] not in '\r\n': i+=2; continue
                if source[i] == quote: i+=1; closed=True; break
                i+=1
            fail(source[start:i],row,col,'Strings não pertencem ao subconjunto.' if closed else 'Texto entre aspas não fechado; strings também estão fora do subconjunto.')
        elif source[i:i+2] in OPERATORS:
            i+=2; emit('OPERADOR',source[start:i],start,row,col)
        elif c in OPERATORS or c in DELIMITERS:
            i+=1;emit('OPERADOR' if c in OPERATORS else 'DELIMITADOR',c,start,row,col)
        else:
            i+=1;fail(c,row,col,f'Caractere não reconhecido: {c!r}. Verifique o subconjunto suportado.')
        column += i-start
    return dict(sucesso=not errors,tokens=tokens,erros=errors)
