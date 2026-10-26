# Registro da Etapa 3

Base: commit ae9d208 da main, preservando arquitetura e correções Docker anteriores.

Comandos previstos: `python -m pytest tests -q`, `docker compose up --build --wait`, `python scripts/smoke.py`, `npm test`.

A suíte anterior foi mantida, com asserções de recepção atualizadas para o contrato léxico. O teste `if ???` foi alterado para `if + :`: interrogações são erros léxicos agora; o novo exemplo continua demonstrando ausência de parser. Texto Unicode entre aspas é preservado, mas corretamente rejeitado como string fora do escopo.

Foram acrescentados testes por palavra reservada, operador, delimitador, identificador, número, erro, recuperação, posições CRLF/tab, comentários e limites; testes reais de tabela e erros no navegador. O Dockerfile agora copia scanner.py. Workflow executa toda a pasta tests.

Resultados da execução: aguardando conclusão; não considerar este registro evidência de aprovação até atualização abaixo.
