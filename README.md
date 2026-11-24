# Compilador Educacional — Etapa 4

Aplicação educacional com scanner e parser de um subconjunto de Python, integrados à API Flask e à interface web. Mostra tokens, árvore sintática abstrata (AST) e diagnósticos com posição. A análise semântica está prevista para a Etapa 5.

- [Gramática em EBNF](docs/gramatica.md)
- [Materiais e Métodos e roteiro de demonstração](docs/metodos-etapa4.md)
- [Registro de testes](docs/testes-etapa4.md)

## Executar

Na pasta deste arquivo, com Docker Desktop iniciado:

```sh
docker compose up --build --wait
```

Abra http://localhost:3000. A porta 3000 deve estar livre. Backend interno em 5000, sem credenciais ou novas variáveis.

```sh
docker compose ps
docker compose logs
docker compose down
```

## Tutorial

1. Selecione um exemplo e clique em Solicitar análise.
2. Compare os lexemas e as posições da tabela com a árvore.
3. Envie `resultado = 10 + 5 * 2` e expanda a atribuição e a adição para ver a multiplicação como operando direito.
4. Digite `x = (10 + 5` para ver um erro sintático com a posição e o elemento esperado.
5. Digite `x = 10 @` para ver um erro léxico com os três tokens válidos preservados.

## Subconjunto léxico

| Categoria | Regra |
|---|---|
| Reservadas | `if`, `else`, sensíveis a maiúsculas |
| Identificadores | ASCII `[A-Za-z_][A-Za-z_0-9]*`; outras palavras são identificadores, não comandos implementados |
| Inteiros | `0` ou `[1-9][0-9]*`; sinal é operador separado |
| Reais | `[0-9]+\.[0-9]+`; sem expoente; exemplo `3.14` |
| Operadores | `+ - * / = == != < > <= >=`; prioridade ao operador de dois caracteres |
| Delimitadores | `(`, `)`, `:` |
| Comentários | `#` até fim da linha; não há comentário de bloco |
| Espaços | Espaço, tab, LF, CR e CRLF ignorados; linhas/colunas começam em 1; tab conta um caractere |
| Fora do escopo | Strings/caracteres entre aspas, Unicode em identificadores, expoentes, bases numéricas, listas, chaves, vírgulas, ponto e vírgula e operadores lógicos |
| Erros | Caractere desconhecido ou literal malformado: acumular erro com localização e continuar |

O reconhecimento é caractere a caractere; expressões regulares apenas validam o literal já agrupado. Implementação própria evita dependências e torna regras e recuperação inspecionáveis. `12abc`, `1.2.3`, `01` e `1.` produzem erro de literal. Aspas são consumidas até fechamento ou fim de linha e diagnosticadas como construção não suportada; texto não fechado recebe mensagem específica. Comentários aceitam Unicode. Um arquivo só de comentários tem sucesso com zero tokens.

Os tokens preservam o contrato do scanner. O parser deriva limites de linha e bloco a partir das posições e da indentação. A implementação é descendente recursiva, em Python e sem dependências de parsing. Reporta o primeiro erro sintático, com o encontrado, a lista de esperados, linha, coluna e mensagem. Com erro léxico, o parser é pulado.

## Contrato HTTP

`POST /api/analisar` recebe JSON como `{"codigo":"x=1"}`. O Nginx encaminha para `/analisar` no backend. Os campos da Etapa 3 permanecem no nível superior, incluindo `etapa: "lexica"`, `sucesso` como estado léxico, `tokens` e `erros`. O campo novo é `sintatico`:

| Entrada | Estado léxico | `sintatico.sucesso` | `sintatico.ast` | `sintatico.erros` |
| --- | --- | --- | --- | --- |
| `x = 1` | Sucesso | `true` | Nó Programa com uma Atribuição | Lista vazia |
| `x =` | Sucesso | `false` | `null` | Diagnóstico de operando faltante |
| `x = @` | Erro | `null` | `null` | Lista vazia |

HTTP 200 indica que a requisição foi processada. Continuam valendo HTTP 400 para entrada inválida, vazia ou acima de 20.000 caracteres, 415 para conteúdo sem JSON, 413 para corpo maior que 512 KiB e 500 para falha interna. As rotas GET `/api/hello` e `/api/health` continuam disponíveis.

## Testes

Python 3.12 e Node 22:

```sh
python -m pip install -r requirements-test.txt
python -m pytest tests -q
npm ci
npx playwright install --with-deps chromium
# Com Docker iniciado:
python scripts/smoke.py
npm test
```

Alternativa local: `python scripts/dev_server.py` (não valida Docker). `BASE_URL` altera endereço dos testes. O workflow executa os testes e valida o Compose. Consulte o [registro da Etapa 4](docs/testes-etapa4.md) para conferir os resultados e o histórico da validação.

## Limitações

A AST cobre a gramática documentada. A interface é navegável e mostra posições. Análise semântica, execução e avaliação com estudantes ficam para trabalhos posteriores.
