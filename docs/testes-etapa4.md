# Registro de testes da Etapa 4

Validação local em 24 de novembro de 2026.

| Comando | Resultado |
| --- | --- |
| `python -m pytest tests -q` | 88 aprovados. Cobre scanner, parser, posições, limites e contrato HTTP. |
| `python scripts/smoke.py` | 9 aprovados com o servidor local do projeto. |
| `npm test` | 22 aprovados em Chromium Headless Shell com o servidor local do projeto. |
| `docker compose config --quiet` e `docker compose up --build --wait` | Validação pelo workflow do GitHub Actions. O ambiente local não dispõe do executável Docker. |

A primeira tentativa com o Chromium do sistema falhou por restrições de criação de sockets. Os testes passaram com o Chromium Headless Shell gerenciado pelo Playwright. Para repetir localmente, instale as dependências e o navegador conforme o README, execute `python scripts/dev_server.py` em um terminal e execute os testes HTTP e de interface em outro.

A execução inicial no GitHub Actions encontrou incompatibilidade entre o Playwright 1.56.1 e o Ubuntu 26.04 do runner padrão. O workflow usa Ubuntu 24.04 e instala o Chromium Headless Shell para os testes de interface.
