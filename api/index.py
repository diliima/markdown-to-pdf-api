from flask import Flask, request, jsonify
import traceback 
import os   
import logging
import uuid
import tempfile
import base64
from datetime import datetime
import sys

# Adiciona o diretório pai ao path para importar o módulo
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from markdown_to_pdf_reportlab import MarkdownToPDFReportLab
except ImportError:
    # Fallback caso o import falhe no Vercel
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'reportlab', 'markdown2'])
    from markdown_to_pdf_reportlab import MarkdownToPDFReportLab

# Configuração de logs para Vercel
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Função principal para o Vercel (sem Flask app)
def handler(event, context):
    """Função principal do Vercel - handler serverless"""
    try:
        # Parse do evento
        path = event.get('path', '/')
        method = event.get('httpMethod', 'GET')
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        # Simula request object
        if body:
            try:
                data = json.loads(body) if body else {}
            except:
                data = {}
        else:
            data = {}
        
        # Roteamento manual
        if path == '/' or path == '/verificar':
            if method == 'GET':
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({
                        "status": "ok", 
                        "message": "API Markdown para PDF está funcionando!",
                        "timestamp": datetime.now().isoformat(),
                        "rotas": [
                            "GET / ou /verificar - Status da API",
                            "POST /converter-markdown-pdf-base64 - Converter MD para PDF"
                        ]
                    })
                }
        
        elif path == '/converter-markdown-pdf-base64' and method == 'POST':
            return converter_markdown_para_pdf_base64_handler(data)
        
        elif path == '/converter-markdown-pdf' and method == 'POST':
            return converter_markdown_para_pdf_base64_handler(data)
        
        # Rota não encontrada
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "status": "erro",
                "mensagem": f"Rota não encontrada: {method} {path}"
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "status": "erro",
                "mensagem": f"Erro interno: {str(e)}"
            })
        }

def converter_markdown_para_pdf_base64_handler(data):
    """Handler para conversão de Markdown para PDF em base64"""
    try:
        # Valida se o texto markdown foi enviado
        if 'texto_markdown' not in data or not data['texto_markdown']:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    "status": "erro",
                    "mensagem": "Campo 'texto_markdown' é obrigatório e não pode estar vazio"
                })
            }
        
        texto_markdown = data['texto_markdown']
        nome_arquivo = data.get('nome_arquivo', f'documento_{uuid.uuid4().hex[:8]}.pdf')
        
        # Garante que o arquivo tem extensão .pdf
        if not nome_arquivo.endswith('.pdf'):
            nome_arquivo += '.pdf'
        
        logger.info(f"Iniciando conversão para arquivo: {nome_arquivo}")
        
        # Cria arquivo temporário para o PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_path = temp_file.name
        
        # Converte o Markdown para PDF
        converter = MarkdownToPDFReportLab()
        sucesso = converter.markdown_text_to_pdf(texto_markdown, temp_path)
        
        if not sucesso:
            # Remove arquivo temporário se falhou
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    "status": "erro",
                    "mensagem": "Falha na conversão do Markdown para PDF"
                })
            }
        
        # Lê o arquivo PDF e converte para base64
        with open(temp_path, 'rb') as pdf_file:
            pdf_content = pdf_file.read()
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
        
        # Remove arquivo temporário
        os.unlink(temp_path)
        
        logger.info(f"Conversão realizada com sucesso: {nome_arquivo} ({len(pdf_content)} bytes)")
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "status": "sucesso",
                "nome_arquivo": nome_arquivo,
                "pdf_base64": pdf_base64,
                "tamanho": len(pdf_content),
                "timestamp": datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        logger.error(f"Erro na conversão: {str(e)}")
        
        # Remove arquivo temporário se houve erro
        try:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
        except Exception:
            pass
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "status": "erro",
                "mensagem": f"Erro interno: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
        }

# Para desenvolvimento local com Flask
if __name__ == "__main__":
    app = Flask(__name__)
    
    @app.route("/", methods=["GET"])
    @app.route("/verificar", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "ok", 
            "message": "API Markdown para PDF está funcionando!",
            "timestamp": datetime.now().isoformat()
        }), 200
    
    app.run(debug=True, port=5000)