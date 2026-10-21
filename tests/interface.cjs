const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const base = process.env.BASE_URL || 'http://127.0.0.1:3000';
(async () => {
 const browser = await chromium.launch({headless:true});
 let passed=0,failed=0;
 async function test(name,fn) {
  const page = await browser.newPage({viewport:{width:1400,height:1000}});
  try { await page.goto(base); await fn(page); passed++; console.log(`PASS ${name}`); }
  catch(e) { failed++; console.error(`FAIL ${name}: ${e.stack}`); }
  finally { await page.close(); }
 }
 async function send(p,code='numero = 10') { await p.locator('#codigo').fill(code); await p.locator('#analisar').click(); }
 async function status(p,expected) { await p.waitForFunction(s => document.querySelector('#estado').dataset.state===s,expected); }
 await test('Elementos principais e linguagem visíveis', async p => {
  for(const id of ['codigo','exemplo','analisar','resultado']) assert(await p.locator('#'+id).isVisible());
  assert((await p.locator('body').innerText()).includes('Python'));
 });
 const examples={variavel:'numero = 10', aritmetica:'valor = 10\nresultado = (valor + 5) * 2', condicional:'numero = 10\nif numero > 0:\n    resultado = numero + 1\nelse:\n    resultado = 0'};
 for(const [key,value] of Object.entries(examples)) await test(`Exemplo ${key}: carregar, editar e enviar`, async p => {
  await p.locator('#codigo').fill('texto anterior'); await p.locator('#exemplo').selectOption(key);
  assert.equal(await p.locator('#codigo').inputValue(),value);
  const edited=value+'\n# edição'; await send(p,edited); await status(p,'success');
  assert.equal(await p.locator('#codigo').inputValue(),edited);
 });
 await test('Trocar exemplo substitui a entrada anterior',async p=>{
  await p.locator('#exemplo').selectOption('variavel');await p.locator('#exemplo').selectOption('condicional');
  assert.equal(await p.locator('#codigo').inputValue(),examples.condicional);
 });
 for(const input of ['', ' \n\t']) await test(`Entrada ${input?'em branco':'vazia'} não envia HTTP`,async p=>{
  let count=0;p.on('request',r=>{if(r.url().endsWith('/api/analisar'))count++;});
  await send(p,input);await status(p,'error');assert.equal(count,0);
  assert((await p.locator('#resultado').innerText()).includes('Informe um código-fonte'));
 });
 await test('Integração real preserva caracteres e indentação',async p=>{
  const code='  texto = "ação 🐍 <script>alert(1)</script>"\n';
  const responsePromise=p.waitForResponse(r=>r.url().endsWith('/api/analisar'));
  await send(p,code);const r=await responsePromise;assert.equal(r.status(),200);
  const data=await r.json();assert.equal(data.codigo,code);assert.equal(data.caracteres,Array.from(code).length);
  await status(p,'success');assert.equal(await p.locator('#codigo').inputValue(),code);
 });
 await test('Código sintaticamente inválido é recebido nesta etapa',async p=>{await send(p,'if ???');await status(p,'success');});
 await test('Limite de tamanho impede envio',async p=>{await send(p,'x'.repeat(20001));await status(p,'error');assert((await p.locator('#resultado').innerText()).includes('20.000'));});
 await test('Falha de rede libera os controles e permite nova tentativa',async p=>{
  await p.route('**/api/analisar',r=>r.abort());await send(p);await status(p,'error');
  assert(await p.locator('#analisar').isEnabled());assert(await p.locator('#codigo').isEditable());
  assert((await p.locator('#resultado').innerText()).includes('Falha de comunicação'));
  await p.unroute('**/api/analisar');await p.locator('#analisar').click();await status(p,'success');
 });
 await test('Erro HTTP 400 mostra orientação do backend como texto seguro',async p=>{
  await p.route('**/api/analisar',r=>r.fulfill({status:400,contentType:'application/json',body:JSON.stringify({mensagem:'Revise <b>o código</b>',recebido:false})}));
  await send(p);await status(p,'error');assert((await p.locator('#resultado').innerText()).includes('<b>o código</b>'));assert.equal(await p.locator('#resultado b').count(),0);
 });
 await test('Erro HTTP 500 não expõe detalhes do servidor',async p=>{
  await p.route('**/api/analisar',r=>r.fulfill({status:500,body:'Traceback /private/password'}));await send(p);await status(p,'error');
  const t=await p.locator('#resultado').innerText();assert(t.includes('erro no servidor'));assert(!t.includes('password'));assert(await p.locator('#analisar').isEnabled());
 });
 for(const body of ['não é JSON',JSON.stringify({recebido:true})]) await test('Resposta inválida não gera falso sucesso',async p=>{
  await p.route('**/api/analisar',r=>r.fulfill({status:200,contentType:'application/json',body}));await send(p);await status(p,'error');
 });
 await test('Envio pendente bloqueia duplicação e preserva o programa',async p=>{
  let release;const gate=new Promise(r=>release=r);let requests=0;
  await p.route('**/api/analisar',async route=>{requests++;await gate;await route.continue();});
  await send(p);await status(p,'loading');assert(await p.locator('#analisar').isDisabled());assert(await p.locator('#exemplo').isDisabled());assert(!(await p.locator('#codigo').isEditable()));
  release();await status(p,'success');assert.equal(requests,1);
 });
 await test('Timeout recupera interface',async p=>{
  await p.clock.install();await p.route('**/api/analisar',()=>{});await send(p);await status(p,'loading');
  await p.clock.fastForward(11000);await status(p,'error');assert(await p.locator('#analisar').isEnabled());
 });
 await test('Regressão HTTP hello e health via proxy',async p=>{
  for(const [url,key,value] of [['hello','message','Hello, World!'],['health','status','ok']]) {
   const r=await p.request.get(base+'/api/'+url);assert.equal(r.status(),200);assert.equal((await r.json())[key],value);
  }
 });
 await test('Layout móvel sem rolagem horizontal',async p=>{
  await p.setViewportSize({width:390,height:844});assert(await p.locator('#codigo').isVisible());
  assert(await p.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
 });
 if (!failed) {
  const p=await browser.newPage({viewport:{width:1400,height:1000},deviceScaleFactor:1});await p.goto(base);
  await p.locator('#exemplo').selectOption('condicional');await p.locator('#analisar').click();await status(p,'success');
  fs.mkdirSync(path.join(__dirname,'../docs/evidencias'),{recursive:true});
  await p.screenshot({path:path.join(__dirname,'../docs/evidencias/interface.png'),fullPage:true});await p.close();
 }
 await browser.close();console.log(`RESULTADO: ${passed} aprovados; ${failed} reprovados`);process.exitCode=failed?1:0;
})().catch(e=>{console.error(e);process.exitCode=1;});
