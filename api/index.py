import json
import os
import sys
import tempfile
import base64
import uuid
from datetime import datetime

# Adiciona o diretório pai ao path para importar o módulo
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from markdown_to_pdf_reportlab import MarkdownToPDFReportLab
except ImportError as e:
    # Se falhar, tenta importar da pasta atual
    try:
        sys.path.insert(0, current_dir)
        from markdown_to_pdf_reportlab import MarkdownToPDFReportLab
    except ImportError:
        # Último recurso - cria uma versão mínima inline
        import subprocess
        import sys
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'reportlab', 'markdown2'])
        from markdown_to_pdf_reportlab import MarkdownToPDFReportLab

def handler(request):
    """Handler principal do Vercel usando a nova assinatura"""
    
    # Headers de resposta padrão
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    try:
        # Parse da requisição do Vercel
        method = request.method
        path = request.path
        
        print(f"Recebida requisição: {method} {path}")  # Log para debug
        
        # Rota de verificação
        if path in ['/', '/verificar'] and method == 'GET':
            response_data = {
                "status": "ok",
                "message": "API Markdown para PDF funcionando no Vercel!",
                "timestamp": datetime.now().isoformat(),
                "path_recebido": path,
                "method_recebido": method,
                "rotas_disponiveis": [
                    "GET / - Status da API",
                    "GET /verificar - Verificação de saúde",
                    "POST /converter-markdown-pdf-base64 - Converter Markdown para PDF"
                ]
            }
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(response_data, ensure_ascii=False)
            }
        
        # Handle OPTIONS for CORS
        elif method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }
        
        # Rota de conversão
        elif path == '/converter-markdown-pdf-base64' and method == 'POST':
            try:
                # Parse do body
                if hasattr(request, 'get_json'):
                    data = request.get_json()
                else:
                    body = request.data if hasattr(request, 'data') else request.body
                    if isinstance(body, bytes):
                        body = body.decode('utf-8')
                    data = json.loads(body) if body else {}
                
            except Exception as parse_error:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        "status": "erro",
                        "mensagem": f"Erro ao parsear JSON: {str(parse_error)}"
                    }, ensure_ascii=False)
                }
            
            # Validação
            if not data or 'texto_markdown' not in data or not data['texto_markdown']:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        "status": "erro",
                        "mensagem": "Campo 'texto_markdown' é obrigatório e não pode estar vazio"
                    }, ensure_ascii=False)
                }
            
            # Conversão
            try:
                texto_markdown = data['texto_markdown']
                nome_arquivo = data.get('nome_arquivo', f'documento_{uuid.uuid4().hex[:8]}.pdf')
                
                if not nome_arquivo.endswith('.pdf'):
                    nome_arquivo += '.pdf'
                
                print(f"Iniciando conversão para: {nome_arquivo}")
                
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
                        'statusCode': 500,
                        'headers': headers,
                        'body': json.dumps({
                            "status": "erro",
                            "mensagem": "Falha na conversão do Markdown para PDF"
                        }, ensure_ascii=False)
                    }
                
                # Lê e converte para base64
                with open(temp_path, 'rb') as pdf_file:
                    pdf_content = pdf_file.read()
                    pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
                
                os.unlink(temp_path)
                
                print(f"Conversão realizada com sucesso: {len(pdf_content)} bytes")
                
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        "status": "sucesso",
                        "nome_arquivo": nome_arquivo,
                        "pdf_base64": pdf_base64,
                        "tamanho": len(pdf_content),
                        "timestamp": datetime.now().isoformat()
                    }, ensure_ascii=False)
                }
                
            except Exception as conv_error:
                print(f"Erro na conversão: {str(conv_error)}")
                
                # Limpa arquivo temporário
                try:
                    if 'temp_path' in locals() and os.path.exists(temp_path):
                        os.unlink(temp_path)
                except:
                    pass
                
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({
                        "status": "erro",
                        "mensagem": f"Erro na conversão: {str(conv_error)}"
                    }, ensure_ascii=False)
                }
        
        # Rota não encontrada
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({
                "status": "erro",
                "mensagem": f"Rota não encontrada: {method} {path}",
                "rotas_disponiveis": ["/", "/verificar", "/converter-markdown-pdf-base64"]
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        print(f"Erro geral: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                "status": "erro",
                "mensagem": f"Erro interno do servidor: {str(e)}"
            }, ensure_ascii=False)
        }

# Para compatibilidade, também exporta como app
from flask import Flask
app = Flask(__name__)

@app.route('/')
@app.route('/verificar')
def health_check():
    return {
        "status": "ok",
        "message": "API Markdown para PDF funcionando!",
        "timestamp": datetime.now().isoformat()
    }

# Para desenvolvimento local
if __name__ == "__main__":
    app.run(debug=True, port=5000)