import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

from config import SERVER_HOST, SERVER_PORT
from functions import (
    init_db,
    buscar_aluno,
    obter_codigo_qr,
    verificar_limite,
    registrar_ocorrencia,
    criar_ticket
)

# Diretório base do projeto (raiz onde estão index.html, frontend, img, etc)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class CatracaRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, status_code: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._send_cors_headers()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path.rstrip("/")

        # Ler corpo JSON
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            payload = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            payload = {}

        # Rotas da API (compatibilidade com /api/* e /backend/api_*)
        if path in ("/api/identificar", "/backend/api_identificar.php"):
            cpf = payload.get("cpf", "").strip()
            if not cpf:
                return self._send_json(400, {"error": "CPF é obrigatório"})
            try:
                aluno = buscar_aluno(cpf)
                return self._send_json(200, {"success": True, "aluno": aluno})
            except Exception as e:
                return self._send_json(500, {"success": False, "error": f"Erro interno: {str(e)}"})

        elif path in ("/api/ocorrencia", "/backend/api_ocorrencia.php"):
            cpf = payload.get("cpf", "").strip()
            tipo = payload.get("tipo", "").strip()
            if not cpf or not tipo:
                return self._send_json(400, {"error": "Campos obrigatórios: cpf, tipo"})
            try:
                permitido = verificar_limite(cpf, tipo)
                if not permitido:
                    return self._send_json(200, {
                        "success": True,
                        "permitido": False,
                        "mensagem": "Limite de ocorrências atingido para este período."
                    })
                registrar_ocorrencia(cpf, tipo)
                return self._send_json(200, {"success": True, "permitido": True})
            except Exception as e:
                return self._send_json(500, {"success": False, "error": f"Erro ao registrar ocorrência: {str(e)}"})

        elif path in ("/api/ticket", "/backend/api_ticket.php"):
            cpf = payload.get("cpf", "").strip()
            tipo = payload.get("tipo", "").strip()
            motivo = payload.get("motivo", "").strip()
            hora = payload.get("hora", "").strip()
            if not cpf or not tipo or not motivo or not hora:
                return self._send_json(400, {"error": "Campos obrigatórios: cpf, tipo, motivo, hora"})
            try:
                qr = obter_codigo_qr(tipo, motivo, hora)
                if qr is None:
                    return self._send_json(200, {
                        "success": True,
                        "ticket": None,
                        "message": "Não é necessário gerar ticket para este horário/tipo."
                    })
                ticket = criar_ticket(cpf, motivo, tipo, qr)
                return self._send_json(200, {"success": True, "ticket": ticket})
            except Exception as e:
                return self._send_json(500, {"success": False, "error": f"Erro ao gerar ticket: {str(e)}"})

        return self._send_json(404, {"error": f"Endpoint não encontrado: {path}"})

    def end_headers(self):
        self._send_cors_headers()
        super().end_headers()

def run_server():
    init_db()
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, CatracaRequestHandler)
    print(f"=== Servidor do Sistema de Catraca Ativo ===")
    print(f"Endereço: http://localhost:{SERVER_PORT}")
    print(f"Pressione Ctrl+C para encerrar.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
        httpd.server_close()

if __name__ == "__main__":
    run_server()

