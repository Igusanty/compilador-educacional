import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
import app as backend
from validation import InvalidInput, validate_payload

@pytest.fixture
def client():
    backend.app.config.update(TESTING=True)
    return backend.app.test_client()

@pytest.mark.parametrize('code', ['numero = 10', 'if numero > 0:\n    numero = numero + 1\n', '  nome = "ação 🐍 <script>"\n', 'if ???'])
def test_preserves_code_without_analysis(client, code):
    r = client.post('/analisar', json={'codigo': code})
    assert r.status_code == 200
    data = r.get_json()
    assert data['codigo'] == code
    assert data['recebido'] is True and data['etapa'] == 'recepcao'
    assert data['caracteres'] == len(code)
    assert data['linhas'] == len(code.splitlines())
    assert 'próximas etapas' in data['mensagem']

@pytest.mark.parametrize('payload,error', [({},'CAMPO_AUSENTE'),([], 'FORMATO_INVALIDO'),(None,'FORMATO_INVALIDO'),({'codigo':None},'TIPO_INVALIDO'),({'codigo':42},'TIPO_INVALIDO'),({'codigo':False},'TIPO_INVALIDO'),({'codigo':[]},'TIPO_INVALIDO'),({'codigo':''},'ENTRADA_VAZIA'),({'codigo':' \n\t'},'ENTRADA_VAZIA'),({'codigo':'x'*20001},'LIMITE_EXCEDIDO')])
def test_invalid_payloads(client, payload, error):
    import json
    r = client.post('/analisar', data=json.dumps(payload), content_type='application/json')
    assert r.status_code == 400
    assert r.get_json()['erro'] == error and r.get_json()['recebido'] is False

@pytest.mark.parametrize('code', ['','\t\n ', 'x'*20001])
def test_validation_unit(code):
    with pytest.raises(InvalidInput): validate_payload({'codigo':code})

def test_limit_boundary(client):
    assert client.post('/analisar',json={'codigo':'x'*20000}).status_code == 200

def test_malformed_json(client):
    r=client.post('/analisar',data='{"codigo":',content_type='application/json')
    assert r.status_code==400 and r.get_json()['erro']=='JSON_INVALIDO'

def test_content_type(client):
    assert client.post('/analisar',data='x').status_code==415

def test_body_limit(client):
    assert client.post('/analisar',data='x'*524289,content_type='application/json').status_code==413

@pytest.mark.parametrize('path,key,value',[('/hello','message','Hello, World!'),('/health','status','ok')])
def test_previous_endpoints(client,path,key,value):
    r=client.get(path)
    assert r.status_code==200 and r.get_json()=={key:value}

@pytest.mark.parametrize('method,path,status',[('get','/analisar',405),('get','/nao-existe',404)])
def test_http_errors(client,method,path,status):
    r=getattr(client,method)(path)
    assert r.status_code==status and r.is_json

def test_unexpected_error_has_no_internal_details(client,monkeypatch):
    def broken(_): raise RuntimeError('/private/path: secret')
    monkeypatch.setattr(backend,'validate_payload',broken)
    r=client.post('/analisar',json={'codigo':'x = 1'})
    assert r.status_code==500 and r.get_json()['erro']=='ERRO_INTERNO'
    assert 'secret' not in r.get_data(as_text=True) and '/private' not in r.get_data(as_text=True)
