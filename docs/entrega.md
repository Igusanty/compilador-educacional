# Como conferir e entregar a segunda etapa

## 1. Atualizar a sua pasta do projeto

Extraia o ZIP. A pasta `compilador-educacional-etapa2` contém todos os arquivos desta versão. Se você já tem o repositório no computador, copie o conteúdo para a pasta dele, substituindo os arquivos existentes e preservando a pasta `.git`. Inclua também `.github` e `.gitignore`.

## 2. Abrir a aplicação

Inicie o Docker Desktop. Abra um terminal na pasta que contém `compose.yaml` e execute:

```bash
docker compose up --build --wait
```

Acesse http://localhost:3000. Não abra somente o arquivo HTML por duplo clique: a comunicação precisa do servidor.

## 3. Demonstrar o funcionamento

1. Mostre o nome do projeto e a linguagem Python.
2. Carregue o exemplo de atribuição e altere `10` para `20`.
3. Clique em Solicitar análise e mostre a confirmação do recebimento.
4. Carregue os outros dois exemplos, verificando a substituição do texto.
5. Apague o código e clique no botão para demonstrar a validação.
6. Envie `if ???` e explique que a análise sintática ainda não existe nesta fase.
7. Selecione o condicional, envie e tire um print da tela com o resultado.

Um print da execução local já está em `docs/evidencias/interface.png`. Depois de executar com Docker, gere uma nova captura para evidenciar seu ambiente de entrega.

## 4. Executar os testes

Siga os comandos do README. Os logs incluídos registram 26 testes do backend, oito de HTTP e 19 de interface aprovados no ambiente local. O Docker e o GitHub Actions também foram validados com sucesso na execução 39524247730, vinculada em `docs/testes.md`. Registre os seus resultados em `docs/testes.md` sem substituir o histórico por resultados que não executou.

## 5. Atualizar o GitHub

Na sua pasta original do repositório, confira antes de enviar:

```bash
git status
git add README.md backend frontend compose.yaml tests scripts docs requirements-test.txt package.json package-lock.json .github .gitignore
git commit -m "Implementa interface, recepcao de codigo e testes da etapa 2"
git push
```

Se o Git solicitar login, autentique-se com sua própria conta. Não coloque senhas ou tokens nos arquivos do projeto. A conexão com o GitHub foi disponibilizada para publicar esta versão. Confira o histórico do repositório e a aba Actions para verificar o commit e a execução dos testes.

Depois do envio, confira a aba Actions e corrija eventuais falhas. Entregue ao professor o link atualizado do repositório e o print solicitado.
