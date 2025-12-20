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
    from markdown_to_docx import MarkdownToDocx
    from json_to_excel import JsonToExcel
    from docx_to_pdf import DocxToPdf
except ImportError:
    # Se não conseguir importar, cria placeholders
    class MarkdownToPDFReportLab:
        def __init__(self):
            pass
        def markdown_text_to_pdf(self, text, path):
            return False
    
    class MarkdownToDocx:
        def __init__(self):
            pass
        def markdown_text_to_docx(self, text, path):
            return False
    
    class JsonToExcel:
        def __init__(self):
            pass
        def json_to_excel_file(self, data, path, sheet_name, apply_formatting):
            return False
        def validate_json_data(self, data):
            return False, "Classe não funcional"
    
    class DocxToPdf:
        def __init__(self):
            pass
        def convert_docx_content_to_pdf(self, content, path):
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
                "message": "API Markdown para PDF, Word e Excel funcionando no Vercel!",
                "timestamp": datetime.now().isoformat(),
                "path": path,
                "method": "GET",
                "rotas_disponiveis": [
                    "GET / - Status da API",
                    "GET /verificar - Verificação de saúde",
                    "POST /converter-markdown-pdf-base64 - Converter Markdown para PDF",
                    "POST /converter-markdown-docx-base64 - Converter Markdown para Word",
                    "POST /converter-json-excel-base64 - Converter JSON para Excel",
                    "POST /converter-docx-pdf-base64 - Converter DOCX/DOC para PDF"
                ]
            }
        else:
            # Rota não encontrada
            self.send_response(404)
            response = {
                "status": "erro",
                "message": f"Rota não encontrada: {path}",
                "rotas_disponiveis": [
                    "/", 
                    "/verificar", 
                    "/converter-markdown-pdf-base64",
                    "/converter-markdown-docx-base64",
                    "/converter-json-excel-base64",
                    "/converter-docx-pdf-base64"
                ]
            }
        
        # Envia resposta
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def do_POST(self):
        """Handle POST requests"""
        
        # Parse da URL
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        try:
            # Verifica o tipo de conteúdo
            content_type = self.headers.get('Content-Type', '')
            
            if 'multipart/form-data' in content_type:
                # Processa multipart/form-data
                import cgi
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )
                data = self._parse_multipart_data(form)
            else:
                # Processa JSON
                content_length = int(self.headers['Content-Length']) if 'Content-Length' in self.headers else 0
                if content_length > 0:
                    post_data = self.rfile.read(content_length)
                    data = json.loads(post_data.decode('utf-8'))
                else:
                    data = {}
            
            # Rotas de conversão
            if path == '/converter-markdown-pdf-base64':
                response = self.handle_pdf_conversion(data)
                status_code = response.get('status_code', 200)
            elif path == '/converter-markdown-docx-base64':
                response = self.handle_docx_conversion(data)
                status_code = response.get('status_code', 200)
            elif path == '/converter-json-excel-base64':
                response = self.handle_excel_conversion(data)
                status_code = response.get('status_code', 200)
            elif path == '/converter-docx-pdf-base64':
                response = self.handle_docx_to_pdf_conversion(data)
                status_code = response.get('status_code', 200)
            else:
                response = {
                    "status": "erro",
                    "message": f"Rota POST não encontrada: {path}",
                    "rotas_disponiveis": [
                        "/converter-markdown-pdf-base64",
                        "/converter-markdown-docx-base64",
                        "/converter-json-excel-base64",
                        "/converter-docx-pdf-base64"
                    ]
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
            self.send_header('Access-Control-Allow-Origin', '*')
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
    
    def _parse_multipart_data(self, form):
        """Parse multipart/form-data"""
        data = {}
        
        for field_name in form.keys():
            field = form[field_name]
            
            if hasattr(field, 'file') and field.file:
                # É um arquivo
                file_content = field.file.read()
                if isinstance(file_content, bytes):
                    # Converte arquivo para base64 
                    import base64
                    data['arquivo_base64'] = base64.b64encode(file_content).decode('utf-8')
                    if hasattr(field, 'filename') and field.filename:
                        data['nome_arquivo_original'] = field.filename
            else:
                # É um campo de texto
                if hasattr(field, 'value'):
                    data[field_name] = field.value
                else:
                    data[field_name] = str(field)
        
        return data
    
    def install_dependencies(self, packages):
        """Tenta instalar dependências necessárias"""
        try:
            import subprocess
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'
            ] + packages, timeout=90)
            return True
        except Exception as e:
            return False
    
    def handle_pdf_conversion(self, data):
        """Handle markdown to PDF conversion"""
        try:
            # Tenta garantir que as dependências estão instaladas
            global MarkdownToPDFReportLab
            try:
                # Testa se a classe funciona
                test_converter = MarkdownToPDFReportLab()
                if not hasattr(test_converter, 'markdown_text_to_pdf'):
                    raise ImportError("Classe não funcional")
            except:
                # Tenta instalar dependências
                if self.install_dependencies(['reportlab==4.4.6', 'markdown2==2.5.4']):
                    try:
                        from markdown_to_pdf_reportlab import MarkdownToPDFReportLab
                    except ImportError as e:
                        return {
                            "status": "erro",
                            "message": f"Erro ao importar após instalação: {str(e)}",
                            "status_code": 500
                        }
                else:
                    return {
                        "status": "erro",
                        "message": "Não foi possível instalar as dependências para PDF",
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
                "message": f"Erro na conversão PDF: {str(e)}",
                "status_code": 500
            }
    
    def handle_docx_conversion(self, data):
        """Handle markdown to Word conversion"""
        try:
            # Tenta garantir que as dependências estão instaladas
            global MarkdownToDocx
            try:
                # Testa se a classe funciona
                test_converter = MarkdownToDocx()
                if not hasattr(test_converter, 'markdown_text_to_docx'):
                    raise ImportError("Classe não funcional")
            except:
                # Tenta instalar dependências
                if self.install_dependencies(['python-docx==1.1.2', 'markdown2==2.5.4']):
                    try:
                        from markdown_to_docx import MarkdownToDocx
                    except ImportError as e:
                        return {
                            "status": "erro",
                            "message": f"Erro ao importar após instalação: {str(e)}",
                            "status_code": 500
                        }
                else:
                    return {
                        "status": "erro",
                        "message": "Não foi possível instalar as dependências para Word",
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
            nome_arquivo = data.get('nome_arquivo', f'documento_{uuid.uuid4().hex[:8]}.docx')
            
            if not nome_arquivo.endswith('.docx'):
                nome_arquivo += '.docx'
            
            # Arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
                temp_path = temp_file.name
            
            # Converte
            converter = MarkdownToDocx()
            sucesso = converter.markdown_text_to_docx(texto_markdown, temp_path)
            
            if not sucesso:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                return {
                    "status": "erro",
                    "message": "Falha na conversão do Markdown para Word",
                    "status_code": 500
                }
            
            # Lê e converte para base64
            with open(temp_path, 'rb') as docx_file:
                docx_content = docx_file.read()
                docx_base64 = base64.b64encode(docx_content).decode('utf-8')
            
            os.unlink(temp_path)
            
            return {
                "status": "sucesso",
                "nome_arquivo": nome_arquivo,
                "docx_base64": docx_base64,
                "tamanho": len(docx_content),
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
                "message": f"Erro na conversão Word: {str(e)}",
                "status_code": 500
            }
    
    def handle_excel_conversion(self, data):
        """Handle JSON to Excel conversion"""
        try:
            # Tenta garantir que as dependências estão instaladas
            global JsonToExcel
            try:
                # Testa se a classe funciona
                test_converter = JsonToExcel()
                if not hasattr(test_converter, 'json_to_excel_file'):
                    raise ImportError("Classe não funcional")
            except:
                # Tenta instalar dependências
                if self.install_dependencies(['pandas==2.2.0', 'openpyxl==3.1.5']):
                    try:
                        from json_to_excel import JsonToExcel
                    except ImportError as e:
                        return {
                            "status": "erro",
                            "message": f"Erro ao importar após instalação: {str(e)}",
                            "status_code": 500
                        }
                else:
                    return {
                        "status": "erro",
                        "message": "Não foi possível instalar as dependências para Excel",
                        "status_code": 500
                    }
            
            # Validação
            if not data or 'dados_json' not in data or not data['dados_json']:
                return {
                    "status": "erro",
                    "message": "Campo 'dados_json' é obrigatório e não pode estar vazio",
                    "status_code": 400
                }
            
            dados_json = data['dados_json']
            nome_arquivo = data.get('nome_arquivo', f'planilha_{uuid.uuid4().hex[:8]}.xlsx')
            nome_aba = data.get('nome_aba', 'Dados')
            aplicar_formatacao = data.get('aplicar_formatacao', True)
            
            if not nome_arquivo.endswith('.xlsx'):
                nome_arquivo += '.xlsx'
            
            # Arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
                temp_path = temp_file.name
            
            # Converte JSON para Excel
            converter = JsonToExcel()
            
            # Valida os dados primeiro
            is_valid, error_msg = converter.validate_json_data(dados_json)
            if not is_valid:
                return {
                    "status": "erro",
                    "message": f"Dados JSON inválidos: {error_msg}",
                    "status_code": 400
                }
            
            sucesso = converter.json_to_excel_file(
                dados_json, 
                temp_path, 
                nome_aba, 
                aplicar_formatacao
            )
            
            if not sucesso:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                return {
                    "status": "erro",
                    "message": "Falha na conversão do JSON para Excel",
                    "status_code": 500
                }
            
            # Lê e converte para base64
            with open(temp_path, 'rb') as excel_file:
                excel_content = excel_file.read()
                excel_base64 = base64.b64encode(excel_content).decode('utf-8')
            
            os.unlink(temp_path)
            
            return {
                "status": "sucesso",
                "nome_arquivo": nome_arquivo,
                "excel_base64": excel_base64,
                "tamanho": len(excel_content),
                "registros": len(dados_json),
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
                "message": f"Erro na conversão Excel: {str(e)}",
                "status_code": 500
            }

    def handle_docx_to_pdf_conversion(self, data):
        """Handle DOCX to PDF conversion"""
        try:
            # Tenta garantir que as dependências estão instaladas
            global DocxToPdf
            try:
                # Testa se a classe funciona
                test_converter = DocxToPdf()
                if not hasattr(test_converter, 'convert_docx_content_to_pdf'):
                    raise ImportError("Classe não funcional")
            except:
                # Tenta instalar dependências
                if self.install_dependencies(['python-docx==1.2.0', 'reportlab==4.4.6']):
                    try:
                        from docx_to_pdf import DocxToPdf
                    except ImportError as e:
                        return {
                            "status": "erro",
                            "message": f"Erro ao importar DocxToPdf após instalação: {str(e)}",
                            "status_code": 500
                        }
                else:
                    return {
                        "status": "erro", 
                        "message": "Falha ao instalar dependências necessárias (python-docx, reportlab)",
                        "status_code": 500
                    }
            
            # Validação dos dados de entrada
            if not isinstance(data, dict):
                return {
                    "status": "erro",
                    "message": "Dados devem ser um objeto JSON",
                    "status_code": 400
                }
            
            if 'arquivo_base64' not in data:
                return {
                    "status": "erro",
                    "message": "Campo 'arquivo_base64' é obrigatório",
                    "status_code": 400
                }
            
            arquivo_base64 = data['arquivo_base64']
            if not arquivo_base64:
                return {
                    "status": "erro",
                    "message": "Campo 'arquivo_base64' não pode estar vazio",
                    "status_code": 400
                }
            
            # Decodifica o arquivo base64
            try:
                arquivo_content = base64.b64decode(arquivo_base64)
                
                # Verifica se o conteúdo parece ser um arquivo DOCX válido
                if not arquivo_content.startswith(b'PK'):
                    return {
                        "status": "erro",
                        "message": "O arquivo enviado não parece ser um arquivo DOCX válido",
                        "status_code": 400
                    }
                    
            except Exception as e:
                return {
                    "status": "erro",
                    "message": f"Erro ao decodificar arquivo base64: {str(e)}",
                    "status_code": 400
                }
            
            nome_arquivo = data.get('nome_arquivo', f'documento_{uuid.uuid4().hex[:8]}.pdf')
            
            if not nome_arquivo.endswith('.pdf'):
                nome_arquivo += '.pdf'
            
            # Arquivo temporário para o PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_path = temp_file.name
            
            # Converte DOCX para PDF
            converter = DocxToPdf()
            sucesso = converter.convert_docx_content_to_pdf(arquivo_content, temp_path)
            
            if not sucesso:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                return {
                    "status": "erro",
                    "message": "Falha na conversão do DOCX para PDF",
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
                "message": f"Erro na conversão DOCX para PDF: {str(e)}",
                "status_code": 500
            }

# Para desenvolvimento local
if __name__ == "__main__":
    from http.server import HTTPServer
    server = HTTPServer(('localhost', 8000), handler)
    print("Servidor rodando em http://localhost:8000")
    print("Rotas disponíveis:")
    print("  GET  / - Status da API")
    print("  GET  /verificar - Health check")
    print("  POST /converter-markdown-pdf-base64 - Converter para PDF")
    print("  POST /converter-markdown-docx-base64 - Converter para Word")
    print("  POST /converter-json-excel-base64 - Converter para Excel")
    server.serve_forever()