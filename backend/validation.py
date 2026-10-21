"""Validação de transporte; não interpreta ou executa código Python."""
MAX_CODE_LENGTH = 20000

class InvalidInput(ValueError):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code

def validate_payload(payload):
    if not isinstance(payload, dict):
        raise InvalidInput('Envie um objeto JSON com o campo codigo.', 'FORMATO_INVALIDO')
    if 'codigo' not in payload:
        raise InvalidInput('O campo codigo é obrigatório.', 'CAMPO_AUSENTE')
    code = payload['codigo']
    if not isinstance(code, str):
        raise InvalidInput('O campo codigo deve ser um texto.', 'TIPO_INVALIDO')
    if not code.strip():
        raise InvalidInput('Informe um código-fonte antes de solicitar a análise.', 'ENTRADA_VAZIA')
    if len(code) > MAX_CODE_LENGTH:
        raise InvalidInput('O código deve ter no máximo 20.000 caracteres.', 'LIMITE_EXCEDIDO')
    return code  # Preserva espaços, indentação e quebras de linha.
