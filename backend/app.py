from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, HTTPException
from validation import InvalidInput, validate_payload

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 512 * 1024
CORS(app)

def error(message, code, status):
    return jsonify(recebido=False, mensagem=message, erro=code), status

@app.get('/hello')
def hello():
    return jsonify(message='Hello, World!')

@app.get('/health')
def health():
    return jsonify(status='ok')

@app.post('/analisar')
def analisar():
    if not request.is_json:
        return error('Envie os dados no formato JSON.', 'CONTEUDO_INVALIDO', 415)
    try:
        payload = request.get_json()
    except BadRequest:
        return error('O JSON enviado está malformado.', 'JSON_INVALIDO', 400)
    try:
        code = validate_payload(payload)
    except InvalidInput as exc:
        return error(str(exc), exc.code, 400)
    return jsonify(
        recebido=True,
        mensagem='Código recebido com sucesso. As análises léxica, sintática e semântica serão implementadas nas próximas etapas.',
        etapa='recepcao', codigo=code,
        caracteres=len(code), linhas=len(code.splitlines()),
    )

@app.errorhandler(HTTPException)
def http_error(exc):
    if exc.code == 413:
        return error('A requisição excede o tamanho permitido.', 'REQUISICAO_GRANDE', 413)
    return error('Requisição não atendida. Verifique o endereço e o método utilizado.', 'ERRO_HTTP', exc.code)

@app.errorhandler(Exception)
def unexpected_error(exc):
    app.logger.exception('Falha inesperada no processamento')
    return error('Ocorreu um erro inesperado. Tente novamente.', 'ERRO_INTERNO', 500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
