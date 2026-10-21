# Registro de testes — Etapa 2

Execução nesta sessão de desenvolvimento. O relógio do executor apresentou 20/10/2026; o contexto da sessão informou 21/10/2026. Os resultados abaixo são os efetivamente obtidos, sem execução remota de CI.

## Resultados

| Camada | Comando | Aprovados | Reprovados | Ambiente |
| --- | --- | --- | --- | --- |
| Unitários, API e regressão | `python3 -m pytest tests/test_backend.py -q` | 26 | 0 | Flask test client |
| Integração HTTP | `python3 scripts/smoke.py` | 8 | 0 | Flask real e proxy Python local |
| Interface e ponta a ponta | `npm test` | 19 | 0 | Chromium Headless Shell, Playwright 1.56.1, servidor local |
| Construção e inicialização Docker | `docker compose up --build --wait` | — | — | Não executado: Docker indisponível |
| Workflow GitHub Actions | push/PR | — | — | Não executado nesta sessão |

Os logs completos estão em `backend-tests.log`, `smoke-tests.log` e `interface-tests.log`. O print `evidencias/interface.png` foi capturado pelo teste de navegador após selecionar e enviar o exemplo condicional ao backend real. Não é uma simulação gráfica. Não é evidência de execução em Docker.

## Cobertura

- Backend: corpo JSON, campo obrigatório, tipo, espaços em branco, limite, preservação do texto, caracteres especiais, JSON malformado, Content-Type, tamanho da requisição, erro inesperado e rotas antigas.
- HTTP: arquivos estáticos, saúde, demonstração, recepção válida e rejeições de entrada.
- Interface: elementos obrigatórios, cada exemplo individualmente, substituição e edição, bloqueio de vazio/limite, integração HTTP real, preservação de caracteres e indentação, código inválido aceito como texto, falhas de rede, recuperação, erros 400/500, resposta incompatível, bloqueio durante envio, timeout e layout móvel.
- Os cenários de falha de rede/servidor usam interceptação controlada no navegador. Os fluxos de sucesso e o print usam a API real.

## Execuções e dificuldades

1. A validação e a API foram verificadas com 26 testes aprovados antes da execução da interface.
2. Uma primeira tentativa HTTP falhou porque o servidor local já havia encerrado. Foi corrigida a execução do processo: servidor e testes passaram a rodar no mesmo ciclo, com encerramento ao final. Os oito testes passaram.
3. A instalação inicial do navegador encontrou arquivos incompletos. Playwright foi fixado em 1.56.1 e a instalação concluiu em uma fonte alternativa usada pelo próprio instalador.
4. O Chromium completo não iniciou devido à restrição de sockets do ambiente. Foi utilizado o modo headless padrão do Playwright. Nenhuma verificação funcional foi removida ou alterada para ocultar falhas.
5. A execução final do backend teve 26 aprovações; a HTTP teve oito; a interface teve 19 e gerou o print. Não houve reprovação funcional nesses conjuntos finais.

## Pendências e limites

O servidor de desenvolvimento não utiliza Nginx: ainda é necessário validar o build, a inicialização, os healthchecks e a comunicação no Compose. O script `scripts/validar-docker.ps1` e o workflow estão preparados para essa verificação. Não se declara a implantação integralmente validada.

Os testes de interface foram executados em Chromium, com verificação de largura móvel. Firefox, Safari, leitores de tela e testes de carga não foram realizados. A implantação de produção não faz parte da etapa. Novos analisadores deverão trazer novos testes sem remover as regressões existentes.
