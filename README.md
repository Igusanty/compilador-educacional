# Compilador Educacional — Etapa 3

Scanner manual em Python, integrado à API Flask e à interface HTML/CSS/JavaScript existente. O scanner produz tokens e acumula erros; não executa programas nem verifica sintaxe ou semântica. Mantidos exemplos, validação, limites, controles de requisição, hello/health e Docker da Etapa 2.

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
2. Compare o texto original com a tabela: tipo é a categoria, lexema é o trecho reconhecido.
3. Observe linha/coluna e contagem por categoria.
4. Digite `x = 10 @` e veja os três tokens válidos e o erro na coluna 8.
5. Digite `if + :`: a tokenização tem sucesso, embora isso não seja um programa sintaticamente válido.

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

Nesta fase, indentação e quebras não viram INDENT/DEDENT/NEWLINE: o código original e posições são preservados. Na Etapa 4 será necessário acrescentar esses tokens ou analisar a disposição do código original para implementar a sintaxe Python. `//` e `**` são sequências de operadores simples, não operadores compostos suportados. Detectar combinações sintaticamente inadequadas cabe ao parser.

## Contrato

`POST /api/analisar`, JSON `{"codigo":"x=1"}`. Nginx encaminha para `/analisar` no backend.

```json
{"recebido":true,"etapa":"lexica","codigo":"x=1","caracteres":3,"linhas":1,"mensagem":"Tokenização concluída.","sucesso":true,"tokens":[{"tipo":"IDENTIFICADOR","lexema":"x","linha":1,"coluna":1,"inicio":0,"fim":1},{"tipo":"OPERADOR","lexema":"=","linha":1,"coluna":2,"inicio":1,"fim":2},{"tipo":"LITERAL_INTEIRO","lexema":"1","linha":1,"coluna":3,"inicio":2,"fim":3}],"erros":[]}
```

Offsets `inicio` inclusivo e `fim` exclusivo contam pontos Unicode, não bytes. Erro léxico mantém HTTP 200, `recebido:true`, `sucesso:false`, tokens válidos e lista `erros`, cada item com `tipo:ERRO_LEXICO`, lexema, linha, coluna e mensagem. HTTP 200 significa requisição processada, não programa válido. Mantidos HTTP 400 para entrada inválida/vazia/maior que 20.000 caracteres, 415 para conteúdo não JSON, 413 para corpo maior que 512 KiB e 500 genérico. Não há stack traces na interface. GET `/api/hello` e `/api/health` preservados.

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

Alternativa local: `python scripts/dev_server.py` (não valida Docker). `BASE_URL` altera endereço dos testes. O workflow executa todos os testes, Docker e integração real. Ver [docs/testes-etapa3.md](docs/testes-etapa3.md) para resultados efetivos. Os registros da Etapa 2 são históricos, não descrevem a implementação atual.

## Limitações

Não há AST, execução, análise sintática/semântica nem avaliação com estudantes. Interface apresenta tabela, totais, explicações e erros em texto seguro; não implementa animação caractere a caractere. Documentação e visualização não são alegadas como inéditas. Usabilidade em celular precisa de estudo com usuários; há teste automatizado de largura de tela.
