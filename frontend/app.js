'use strict';
const examples = {
  variavel: 'numero = 10',
  aritmetica: 'valor = 10\nresultado = (valor + 5) * 2',
  condicional: 'numero = 10\nif numero > 0:\n    resultado = numero + 1\nelse:\n    resultado = 0'
};
const editor = document.querySelector('#codigo');
const selector = document.querySelector('#exemplo');
const button = document.querySelector('#analisar');
const result = document.querySelector('#resultado');
const state = document.querySelector('#estado');
const count = document.querySelector('#contador');
function updateCount() { count.textContent = `${Array.from(editor.value).length} caracteres`; }
function show(kind, title, message, data) {
  state.dataset.state = kind;
  state.textContent = { idle: 'Aguardando', loading: 'Enviando', success: 'Recebido', error: 'Atenção' }[kind];
  result.replaceChildren();
  const heading = document.createElement('h3'); heading.textContent = title;
  const body = document.createElement('p'); body.textContent = message;
  result.append(heading, body);
  if (data) {
    const metrics = document.createElement('div'); metrics.className = 'metrics';
    for (const [value, label] of [[data.linhas, 'linhas recebidas'], [data.caracteres, 'caracteres recebidos']]) {
      const item = document.createElement('div'); item.className = 'metric';
      const number = document.createElement('strong'); number.textContent = value;
      const caption = document.createElement('span'); caption.textContent = label;
      item.append(number, caption); metrics.append(item);
    }
    result.append(metrics);
  }
}
editor.addEventListener('input', updateCount);
selector.addEventListener('change', () => {
  if (!(selector.value in examples)) return;
  editor.value = examples[selector.value]; updateCount(); editor.focus();
  show('idle', 'Exemplo carregado', 'Edite o código se desejar e solicite a análise.');
});
button.addEventListener('click', async () => {
  const code = editor.value;
  if (!code.trim()) { show('error', 'Insira um programa', 'Informe um código-fonte antes de solicitar a análise.'); editor.focus(); return; }
  if (Array.from(code).length > 20000) { show('error', 'Código muito longo', 'O código deve ter no máximo 20.000 caracteres.'); return; }
  button.disabled = true; selector.disabled = true; editor.readOnly = true;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10000);
  show('loading', 'Enviando código…', 'Aguardando a resposta do servidor.');
  try {
    const response = await fetch('/api/analisar', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({codigo: code}), signal: controller.signal
    });
    if (response.status >= 500) { show('error', 'Servidor indisponível', 'Ocorreu um erro no servidor. Tente novamente.'); return; }
    const data = await response.json();
    if (!response.ok) {
      show('error', 'Entrada não aceita', typeof data.mensagem === 'string' ? data.mensagem : 'Não foi possível processar a entrada. Revise o código e tente novamente.'); return;
    }
    if (data.recebido !== true || data.etapa !== 'lexica' || !data.sintatico || !Array.isArray(data.sintatico.erros) || !Array.isArray(data.tokens) || !Array.isArray(data.erros) || typeof data.sucesso !== 'boolean' || typeof data.mensagem !== 'string' || !Number.isInteger(data.linhas) || !Number.isInteger(data.caracteres)) {
      throw new Error('Resposta incompatível');
    }
    const syntax = data.sintatico;
    if (!data.sucesso) {
      show('error', 'Erros léxicos encontrados', data.mensagem + ' A análise sintática não foi executada.', data);
    } else if (!syntax.sucesso) {
      show('error', 'Erro sintático encontrado', 'Os tokens foram reconhecidos. Revise a estrutura do programa.', data);
    } else {
      show('success', 'Análise sintática concluída', 'Confira os tokens e a estrutura do programa na árvore.', data);
    }
    renderTokens(data);
    renderSyntax(syntax);
  } catch (_) {
    show('error', 'Falha de comunicação', 'Não foi possível comunicar com o servidor. Verifique a conexão e tente novamente.');
  } finally {
    clearTimeout(timer); button.disabled = false; selector.disabled = false; editor.readOnly = false;
  }
});
updateCount();

function renderTokens(data) {
  const info=document.createElement('p');
  info.textContent='Token é a categoria; lexema é o trecho exato do código. Linha e coluna começam em 1. O parser usa esses tokens para verificar a estrutura do programa.';
  result.append(info);
  const summary=document.createElement('p'); const groups={};
  for(const t of data.tokens) groups[t.tipo]=(groups[t.tipo]||0)+1;
  summary.textContent=`${data.tokens.length} tokens: `+Object.entries(groups).map(([k,v])=>`${k}: ${v}`).join(' · '); result.append(summary);
  const wrap=document.createElement('div');wrap.className='token-scroll';
  const table=document.createElement('table');table.id='tokens';
  const caption=document.createElement('caption');caption.textContent='Tokens na ordem do código';table.append(caption);
  const head=document.createElement('thead'); const hr=document.createElement('tr');
  for(const label of ['Tipo','Lexema','Linha','Coluna']) {const th=document.createElement('th');th.scope='col';th.textContent=label;hr.append(th);}head.append(hr);table.append(head);
  const body=document.createElement('tbody');
  for(const token of data.tokens) {const row=document.createElement('tr'); for(const key of ['tipo','lexema','linha','coluna']){const cell=document.createElement('td');cell.textContent=token[key];row.append(cell);}body.append(row);}
  table.append(body);wrap.append(table);result.append(wrap);
  const errors=document.createElement('ul');errors.id='erros-lexicos';
  for(const e of data.erros){const item=document.createElement('li');item.textContent=`Linha ${e.linha}, coluna ${e.coluna}: ${e.mensagem} Trecho: ${e.lexema}`;errors.append(item);}result.append(errors);
}

function renderSyntax(syntax) {
  if (syntax.sucesso === null) return;
  const section = document.createElement('section');
  const title = document.createElement('h4');
  section.append(title);
  result.append(section);
  if (!syntax.sucesso) {
    title.textContent = 'Diagnóstico sintático';
    const list = document.createElement('ul');
    list.id = 'erros-sintaticos';
    for (const error of syntax.erros) {
      const item = document.createElement('li');
      item.textContent = `Linha ${error.linha}, coluna ${error.coluna}: ${error.mensagem}`;
      list.append(item);
    }
    section.append(list);
    return;
  }
  title.textContent = 'Árvore sintática abstrata (AST)';
  const help = document.createElement('p');
  help.textContent = 'Expanda os nós para ver como as partes do programa se relacionam.';
  const tree = document.createElement('div');
  tree.id = 'ast';
  tree.append(renderNode(syntax.ast, true));
  section.append(help, tree);
}

function renderNode(node, open = false) {
  const labels = {
    Programa: 'Programa', Atribuicao: 'Atribuição', Condicional: 'Condicional',
    Bloco: 'Bloco', Comparacao: 'Comparação', OperacaoBinaria: 'Operação binária',
    OperacaoUnaria: 'Operação unária', Identificador: 'Identificador',
    Inteiro: 'Inteiro', Real: 'Real'
  };
  const detail = node.operador ?? node.nome ?? node.valor;
  const label = node.filhos.length ? document.createElement('summary') : document.createElement('div');
  label.textContent = `${labels[node.tipo]}${detail === undefined ? '' : ' ' + detail} (linha ${node.linha}, coluna ${node.coluna})`;
  if (!node.filhos.length) return label;
  const group = document.createElement('details');
  group.open = open;
  group.append(label);
  for (const child of node.filhos) group.append(renderNode(child));
  return group;
}
