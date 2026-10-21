"""Teste HTTP do ambiente iniciado pelo Compose (ou servidor local)."""
import json
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError
BASE = os.getenv('BASE_URL', 'http://localhost:3000').rstrip('/')
passed = 0

def check(path, expected, payload=None, key=None, value=None):
    global passed
    data = None if payload is None else json.dumps(payload).encode()
    req = Request(BASE + path, data=data, headers={'Content-Type':'application/json'})
    try:
        with urlopen(req, timeout=15) as response:
            status, body = response.status, response.read()
    except HTTPError as response:
        status, body = response.code, response.read()
    assert status == expected, (path, status, expected)
    if key is not None: assert json.loads(body)[key] == value
    passed += 1
    print(f'PASS {path}: HTTP {status}')

check('/',200)
check('/styles.css',200)
check('/app.js',200)
check('/api/health',200,key='status',value='ok')
check('/api/hello',200,key='message',value='Hello, World!')
check('/api/analisar',200,{'codigo':'numero = 10'},'recebido',True)
check('/api/analisar',400,{'codigo':' \n\t'},'erro','ENTRADA_VAZIA')
check('/api/analisar',400,{},'erro','CAMPO_AUSENTE')
print(f'RESULTADO: {passed} aprovados; 0 reprovados')
