# Gramática do subconjunto de Python

O símbolo inicial é `programa`. Os nomes à esquerda de `=` são não terminais. As palavras e os símbolos entre aspas são terminais, assim como as categorias e marcas estruturais em maiúsculas.

```ebnf
programa    = { comando }, EOF ;
comando     = atribuicao | condicional ;
atribuicao  = IDENTIFICADOR, "=", expressao, NEWLINE ;
condicional = "if", expressao, ":", NEWLINE, bloco,
              [ "else", ":", NEWLINE, bloco ] ;
bloco       = INDENT, comando, { comando }, DEDENT ;
expressao   = soma, [ ("==" | "!=" | "<" | "<=" | ">" | ">="), soma ] ;
soma        = produto, { ("+" | "-"), produto } ;
produto     = fator, { ("*" | "/"), fator } ;
fator       = ("+" | "-"), fator
            | IDENTIFICADOR | LITERAL_INTEIRO | LITERAL_REAL
            | "(", expressao, ")" ;
```

| Terminais | Origem |
| --- | --- |
| `IDENTIFICADOR`, `LITERAL_INTEIRO`, `LITERAL_REAL` | Categorias do scanner |
| `if`, `else` | Lexemas da categoria `PALAVRA_RESERVADA` |
| `=`, `+`, `-`, `*`, `/` e operadores de comparação | Lexemas da categoria `OPERADOR` |
| `(`, `)`, `:` | Lexemas da categoria `DELIMITADOR` |
| `NEWLINE`, `INDENT`, `DEDENT`, `EOF` | Limites derivados pelo parser das linhas, da indentação e do comprimento do código |

O parser agrupa os tokens por linha. O fim de uma linha com tokens termina o comando, inclusive na última linha sem quebra explícita. Linhas em branco e linhas só com comentários não afetam os blocos. No nível do programa, os comandos começam sem recuo. O primeiro comando após um cabeçalho define o recuo do bloco, em espaços, maior que o do cabeçalho. Os comandos irmãos usam esse mesmo recuo. O `else` tem a indentação do `if` correspondente. São aceitos LF, CRLF e CR.

Da maior para a menor precedência vêm os grupos entre parênteses, os sinais unários, a multiplicação e divisão, a soma e subtração e a comparação. Os operadores aritméticos binários associam à esquerda. Sinais unários podem se aninhar. Cada expressão admite uma comparação direta. Comparações encadeadas ficam fora do subconjunto.

| Entrada | Resultado |
| --- | --- |
| `x = 10 + 5 * 2` | A adição tem a multiplicação como operando direito. |
| `x = 20 - 5 - 3` | A subtração à esquerda vira o primeiro operando da segunda subtração. |
| `x = (10 + 5) * 2` | A multiplicação tem a adição como operando esquerdo. |
| `x = (10 + 5` | Diagnóstico de parêntese ausente. |
| `if x:` no fim do arquivo | Diagnóstico de bloco indentado ausente. |
| `else:` sem condicional | Diagnóstico de `if` ausente. |

```python
resultado = 10 + 5 * 2
if resultado > 10:
    resultado = resultado - 1
else:
    resultado = 0
```

O escopo cobre atribuições simples, expressões numéricas e relacionais e blocos condicionais aninhados. Ficam fora do escopo expressões como comandos, comandos multilinha, tabulações no recuo, vários comandos na mesma linha, `elif`, laços, funções, strings, estruturas de dados, operadores lógicos e análise semântica.

O limite da API continua sendo 20.000 caracteres. O parser aceita até 128 tokens em uma linha, 24 níveis de blocos e profundidade de fator inferior a 24, contando parênteses e sinais unários. Esses limites restringem a profundidade da recursão e da serialização da AST. Um programa só com comentários é válido e produz uma AST vazia. Entradas vazias ou só com espaços continuam sujeitas à validação HTTP da API.
