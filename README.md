# Compilador Educacional

## Objetivo
Criar uma aplicação web educacional para apoiar o aprendizado de conceitos de compiladores, com foco inicial na análise de pequenos trechos de código Python. Nesta primeira etapa, a aplicação apenas demonstra a comunicação entre frontend e backend.

## Linguagem e subconjunto inicial
A linguagem escolhida para estudo é **Python**. O subconjunto planejado para as próximas etapas inclui:
- Atribuição de variáveis, como `idade = 20`.
- Operadores aritméticos: `+`, `-`, `*` e `/`.
- Estruturas condicionais `if` e `else`.

Python foi escolhida por ter sintaxe relativamente simples e permitir exemplos curtos, adequados para apresentar conceitos de análise léxica, sintática e semântica. **Essas análises ainda não foram implementadas.**

## Estrutura
- `frontend/`: página web estática e configuração do Nginx.
- `backend/`: API Flask que retorna a mensagem "Hello, World!".
- `compose.yaml`: configuração dos serviços Docker.

## Pré-requisitos
- Docker Desktop com Docker Engine em execução.
- Docker Compose v2 (incluído nas instalações atuais do Docker Desktop).
- Git, caso queira enviar o projeto ao GitHub.

Verifique as versões instaladas:
```bash
docker --version
docker compose version
```

## Executar
Na pasta raiz do projeto:
```bash
docker compose up --build -d
```
Abra http://localhost:3000 no navegador. A página deve mostrar **Hello, World!**, recebida do backend.

Para verificar diretamente a API: http://localhost:3000/api/hello

Para visualizar logs:
```bash
docker compose logs
```

## Encerrar
```bash
docker compose down
```

## Teste de instalação limpa
1. Clone o repositório em uma pasta nova: `git clone URL_DO_SEU_REPOSITORIO`.
2. Entre na pasta: `cd compilador-educacional`.
3. Execute `docker compose up --build -d`.
4. Acesse http://localhost:3000 e confira a mensagem "Hello, World!".
5. Acesse http://localhost:3000/api/health e confira o retorno `{"status":"ok"}`.
6. Encerre com `docker compose down`.

**Importante:** substitua `URL_DO_SEU_REPOSITORIO` pelo endereço real do seu repositório. Registre a validação somente depois de realizar os testes.

## Estado atual
Primeira etapa: estrutura inicial preparada. Os testes de execução e instalação limpa devem ser realizados na máquina de quem entrega o projeto.
