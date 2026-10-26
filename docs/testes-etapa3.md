# Registro da Etapa 3

Base: commit ae9d208 da main, preservando arquitetura e correções Docker anteriores.

Comandos previstos: `python -m pytest tests -q`, `docker compose up --build --wait`, `python scripts/smoke.py`, `npm test`.

A suíte anterior foi mantida, com asserções de recepção atualizadas para o contrato léxico. O teste `if ???` foi alterado para `if + :`: interrogações são erros léxicos agora; o novo exemplo continua demonstrando ausência de parser. Texto Unicode entre aspas é preservado, mas corretamente rejeitado como string fora do escopo.

Foram acrescentados testes por palavra reservada, operador, delimitador, identificador, número, erro, recuperação, posições CRLF/tab, comentários e limites; testes reais de tabela e erros no navegador. O Dockerfile agora copia scanner.py. Workflow executa toda a pasta tests.

## Resultados verificados em 26/10/2026

Commit de implementação: dffa43582de948b81feed4e8ec57cfd25a14cfd1.
Execução: https://github.com/Igusanty/compilador-educacional/actions/runs/40352212145

- `python -m pytest tests -q`: 66 testes aprovados.
- `docker compose config --quiet`: aprovado.
- `docker compose up --build --wait`: backend e frontend Healthy.
- `python scripts/smoke.py`: 8 testes HTTP aprovados.
- `npm test`: 21 testes de navegador aprovados, incluindo tabela, recuperação de erros, exemplos, edição, rede, timeout e largura móvel.
- Total: 95 testes, zero falhas; artefato evidencia-interface contém captura da demonstração.
- `docker compose down`: concluído.

O ambiente local não tinha Docker e perdeu o interpretador do ambiente virtual entre sessões; por isso a validação reproduzível completa foi executada no Ubuntu do GitHub Actions com Python 3.12, Node 22 e Docker. A instalação local anterior aprovou os 66 testes Python. Não se afirma execução Docker no computador pessoal do aluno nem avaliação pedagógica com estudantes.

Correções: inclusão de scanner.py no Dockerfile, execução da suíte completa no workflow e atualização das expectativas antigas do contrato recepcao para lexica. Nenhuma falha funcional foi encontrada na execução completa registrada acima. Este commit posterior altera apenas o registro dos resultados.