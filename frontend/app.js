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
    if (data.recebido !== true || data.etapa !== 'recepcao' || typeof data.mensagem !== 'string' || !Number.isInteger(data.linhas) || !Number.isInteger(data.caracteres)) {
      throw new Error('Resposta incompatível');
    }
    show('success', 'Código recebido!', data.mensagem, data);
  } catch (_) {
    show('error', 'Falha de comunicação', 'Não foi possível comunicar com o servidor. Verifique a conexão e tente novamente.');
  } finally {
    clearTimeout(timer); button.disabled = false; selector.disabled = false; editor.readOnly = false;
  }
});
updateCount();
