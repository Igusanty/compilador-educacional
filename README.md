# Compilador Educacional — Etapa 2

Aplicação educacional para estudantes experimentarem a entrada de programas de um subconjunto de **Python**. Esta versão recebe o código, valida a entrada e confirma o recebimento. **Ainda não executa programas nem realiza análise léxica, sintática ou semântica.**

Continuação da primeira etapa: HTML/CSS/JavaScript servido por Nginx, backend Python/Flask e Docker Compose. As rotas anteriores de demonstração e saúde foram preservadas.

## Executar com Docker

Instale e inicie o Docker Desktop (ou Docker Engine com Compose v2). Na pasta que contém `compose.yaml`:

```bash
docker compose up --build --wait
```

Abra **http://localhost:3000**. Para verificar os serviços e encerrar:

```bash
docker compose ps
docker compose logs
docker compose down
```

A porta 3000 deve estar disponível. O backend é acessado internamente pelo Nginx, sem publicar a porta 5000. O navegador chama `/api/analisar`; o Nginx encaminha a chamada para `backend:5000/analisar` na rede do Compose. Não são necessárias credenciais nem variáveis de ambiente.

## Usar a interface

1. Escolha um dos três exemplos ou digite um programa.
2. Edite o conteúdo, se desejar. Escolher outro exemplo substitui o texto atual.
3. Clique em **Solicitar análise**.
4. Confira a confirmação e a quantidade de linhas e caracteres recebidos.

O código permanece no editor após o envio. Entradas vazias e com mais de 20.000 caracteres são recusadas. Durante a requisição, os controles ficam bloqueados para evitar duplicações. Falhas de rede, respostas inválidas e espera superior a dez segundos mostram uma mensagem e liberam nova tentativa. Recarregar a página apaga o conteúdo: não há persistência.

## Linguagem e exemplos

O subconjunto previsto inclui atribuições, números, identificadores, operações `+`, `-`, `*`, `/`, parênteses e condicionais `if/else`. A comparação `>` integra o exemplo condicional planejado. A validade dessas construções será verificada nas etapas futuras.

**1. Atribuição de variável**

```python
numero = 10
```

**2. Operações aritméticas**

```python
valor = 10
resultado = (valor + 5) * 2
```

**3. Condicional**

```python
numero = 10
if numero > 0:
    resultado = numero + 1
else:
    resultado = 0
```

## Contrato da API

`POST /api/analisar`, com cabeçalho `Content-Type: application/json`:

```json
{"codigo":"numero = 10"}
```

Resposta HTTP 200:

```json
{
  "recebido": true,
  "mensagem": "Código recebido com sucesso. As análises léxica, sintática e semântica serão implementadas nas próximas etapas.",
  "etapa": "recepcao",
  "codigo": "numero = 10",
  "caracteres": 11,
  "linhas": 1
}
```

`codigo` é preservado, inclusive espaços e indentação. `caracteres` conta pontos de código Unicode; `linhas` usa `str.splitlines()` do Python, sem contar uma linha vazia adicional por quebra final. O recebimento não confirma que o programa esteja correto: texto como `if ???` também é recebido.

Resposta de erro, por exemplo HTTP 400:

```json
{"recebido":false,"mensagem":"Informe um código-fonte antes de solicitar a análise.","erro":"ENTRADA_VAZIA"}
```

| HTTP | Situação |
| --- | --- |
| 400 | JSON malformado; corpo que não é objeto; `codigo` ausente, não textual, vazio ou acima de 20.000 caracteres |
| 415 | Tipo de conteúdo diferente de JSON |
| 413 | Corpo da requisição acima de 512 KiB no Flask |
| 500 | Erro inesperado, com mensagem genérica para o usuário |

As rotas `GET /api/hello` e `GET /api/health` continuam disponíveis. Diretamente no backend, os caminhos não incluem `/api`. Não há banco de dados, execução ou gravação dos programas enviados.

## Testes automatizados

Requisitos para testes: Python 3.12, Node.js 22 e npm. Na raiz:

```bash
python -m pip install -r requirements-test.txt
python -m pytest tests/test_backend.py -q
npm ci
npx playwright install chromium
```

Com a aplicação iniciada pelo Compose:

```bash
python scripts/smoke.py
npm test
```

Em Linux, se faltarem bibliotecas do navegador, use `npx playwright install --with-deps chromium`. `BASE_URL` permite apontar os testes HTTP e de interface para outro endereço. A execução bem-sucedida da interface salva `docs/evidencias/interface.png`.

No Windows, `powershell -ExecutionPolicy Bypass -File scripts/validar-docker.ps1` valida a configuração, inicia o Compose e executa os oito testes HTTP (requer Python). Depois, execute `npm test` para os testes de navegador.

Para desenvolvimento sem Docker, execute `python scripts/dev_server.py` em um terminal e os testes em outro. Esse servidor local usa Flask e um proxy Python e **não comprova a implantação Nginx/Docker**.

O workflow `.github/workflows/tests.yml` está preparado para executar backend, construção e inicialização do Docker, smoke e navegador a cada push/PR. Sua presença não significa que uma execução remota tenha ocorrido. Consulte os resultados efetivos e limitações em [docs/testes.md](docs/testes.md).

## Organização

- `frontend/`: interface, exemplos, comunicação HTTP e configuração Nginx.
- `backend/`: API Flask e módulo de validação.
- `tests/`: validações, endpoints, integração, interface e regressões.
- `scripts/`: servidor local de teste e verificação de implantação.
- `docs/`: registros dos testes e evidência visual.

## Limitações e próximas etapas

A versão atual é destinada ao ambiente educacional local. O servidor Flask mantido da primeira etapa não constitui uma configuração de produção. O conteúdo não é salvo entre sessões. Não existem tokens, árvore sintática, tabela de símbolos ou verificação semântica. Os próximos analisadores deverão ser acrescentados progressivamente, preservando os testes existentes e documentando mudanças no contrato.

## Demonstração e entrega

Veja [docs/entrega.md](docs/entrega.md) para o roteiro da demonstração, atualização do repositório e pendências de validação.
