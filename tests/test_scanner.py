import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
import pytest
from scanner import scan, KEYWORDS, OPERATORS, DELIMITERS
@pytest.mark.parametrize('word',sorted(KEYWORDS))
def test_keywords(word): assert scan(word)['tokens'][0]['tipo']=='PALAVRA_RESERVADA'
@pytest.mark.parametrize('op',sorted(OPERATORS|DELIMITERS))
def test_symbols(op):
 r=scan(op);assert r['sucesso'] and [t['lexema'] for t in r['tokens']]==[op]
@pytest.mark.parametrize('text',['a','_x1','ifx','numero2','0','42','3.14'])
def test_valid(text): assert scan(text)['sucesso'] and len(scan(text)['tokens'])==1
@pytest.mark.parametrize('text',['12abc','1.2.3','1.','01','@','á','"abc','"abc"','$'])
def test_invalid(text):
 r=scan(text);assert not r['sucesso'];assert r['erros'][0]['linha']==1 and r['erros'][0]['coluna']==1
@pytest.mark.parametrize('text',['',' \t\n','# comentário','\r\n# bloco não existe\r'])
def test_empty(text): assert scan(text)==dict(sucesso=True,tokens=[],erros=[])
def test_positions_and_recovery():
 r=scan('x=1\r\n\t@ y<=2 #fim\r\nz')
 assert [(t['lexema'],t['linha'],t['coluna']) for t in r['tokens']]==[('x',1,1),('=',1,2),('1',1,3),('y',2,4),('<=',2,5),('2',2,7),('z',3,1)]
 assert r['erros'][0]['coluna']==2
 assert scan('@ x $')['tokens'][0]['lexema']=='x'
def test_not_parser():assert scan('if + :')['sucesso']
def test_string_recovery():assert scan('"bad\nx=1')['tokens'][0]['linha']==2
def test_endpoints():
 from app import app
 c=app.test_client()
 for code,success in [('x=1',True),('@x$',False),('# comentário',True),('if + :',True)]:
  r=c.post('/analisar',json={'codigo':code});assert r.status_code==200
  assert r.json['sucesso']==success and isinstance(r.json['tokens'],list)
