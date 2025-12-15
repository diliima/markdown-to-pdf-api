from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import tempfile
import base64
import uuid
from datetime import datetime
import urllib.parse

# Adiciona o diretório pai ao path para importar o módulo
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, current_dir)

try:
    from markdown_to_pdf_reportlab import MarkdownToPDFReportLab
except ImportError:
    # Se não conseguir importar, cria um placeholder
    class MarkdownToPDFReportLab:
        def __init__(self):
            pass
        def markdown_text_to_pdf(self, text, path):
            # Placeholder - vai tentar instalar as dependências depois
            return False

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        
        # Parse da URL
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Headers de resposta
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Rota de verificação
        if path in ['/', '/verificar']:
            response = {
                "status": "ok",
                "message": "API Markdown para PDF funcionando no Vercel!",
                "timestamp": datetime.now().isoformat(),
                "path": path,
                "method": "GET",
                "rotas_disponiveis": [
                    "GET / - Status da API",
                    "GET /verificar - Verificação de saúde",
                    "POST /converter-markdown-pdf-base64 - Converter Markdown para PDF"
                ]
            }
        else:
            # Rota não encontrada
            self.send_response(404)
            response = {
                "status": "erro",
                "message": f"Rota não encontrada: {path}",
                "rotas_disponiveis": ["/", "/verificar", "/converter-markdown-pdf-base64"]
            }
        
        # Envia resposta
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def do_POST(self):
        """Handle POST requests"""
        
        # Parse da URL
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        try:
            # Lê o body da requisição
            content_length = int(self.headers['Content-Length']) if 'Content-Length' in self.headers else 0
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
            else:
                data = {}
            
            # Rota de conversão
            if path == '/converter-markdown-pdf-base64':
                response = self.handle_conversion(data)
                status_code = response.get('status_code', 200)
            else:
                response = {
                    "status": "erro",
                    "message": f"Rota POST não encontrada: {path}"
                }
                status_code = 404
            
            # Envia resposta
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Remove status_code da resposta antes de enviar
            if 'status_code' in response:
                del response['status_code']
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_response = {
                "status": "erro",
                "message": f"Erro no servidor: {str(e)}"
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def handle_conversion(self, data):
        """Handle markdown to PDF conversion"""
        try:
            # Tenta importar novamente se necessário
            global MarkdownToPDFReportLab
            if not hasattr(MarkdownToPDFReportLab, 'markdown_text_to_pdf') or \
               MarkdownToPDFReportLab().markdown_text_to_pdf("test", "/tmp/test") == False:
                try:
                    import subprocess
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'reportlab==4.2.2', 'markdown2==2.5.0'])
                    # Reimporta após instalar
                    from markdown_to_pdf_reportlab import MarkdownToPDFReportLab
                except Exception as install_error:
                    return {
                        "status": "erro",
                        "message": f"Erro ao instalar dependências: {str(install_error)}",
                        "status_code": 500
                    }
            
            # Validação
            if not data or 'texto_markdown' not in data or not data['texto_markdown']:
                return {
                    "status": "erro",
                    "message": "Campo 'texto_markdown' é obrigatório e não pode estar vazio",
                    "status_code": 400
                }
            
            texto_markdown = data['texto_markdown']
            nome_arquivo = data.get('nome_arquivo', f'documento_{uuid.uuid4().hex[:8]}.pdf')
            
            if not nome_arquivo.endswith('.pdf'):
                nome_arquivo += '.pdf'
            
            # Arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_path = temp_file.name
            
            # Converte
            converter = MarkdownToPDFReportLab()
            sucesso = converter.markdown_text_to_pdf(texto_markdown, temp_path)
            
            if not sucesso:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                return {
                    "status": "erro",
                    "message": "Falha na conversão do Markdown para PDF",
                    "status_code": 500
                }
            
            # Lê e converte para base64
            with open(temp_path, 'rb') as pdf_file:
                pdf_content = pdf_file.read()
                pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
            
            os.unlink(temp_path)
            
            return {
                "status": "sucesso",
                "nome_arquivo": nome_arquivo,
                "pdf_base64": pdf_base64,
                "tamanho": len(pdf_content),
                "timestamp": datetime.now().isoformat(),
                "status_code": 200
            }
            
        except Exception as e:
            # Limpa arquivo temporário se houver erro
            try:
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    os.unlink(temp_path)
            except:
                pass
            
            return {
                "status": "erro",
                "message": f"Erro na conversão: {str(e)}",
                "status_code": 500
            }

# Para desenvolvimento local
if __name__ == "__main__":
    from http.server import HTTPServer
    server = HTTPServer(('localhost', 8000), handler)
    print("Servidor rodando em http://localhost:8000")
    server.serve_forever()