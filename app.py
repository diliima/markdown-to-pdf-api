from flask import Flask, request, jsonify, send_file, make_response
# Importa as funções principais e URL
from markdown_to_pdf_reportlab import MarkdownToPDFReportLab
from markdown_to_docx import MarkdownToDocx
import traceback 
import os   
import logging
import uuid
import tempfile
from logging.handlers import RotatingFileHandler
from datetime import datetime
from io import BytesIO


# Inicializa o app Flask
app = Flask(__name__)
# Configuração de logs
    


@app.route("/verificar", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200


@app.route("/converter-markdown-pdf", methods=["POST"])
def converter_markdown_para_pdf_api():
    """Converte texto Markdown para PDF via API.
    
    Espera JSON com:
    {
        "texto_markdown": "# Título\nConteúdo...",
        "nome_arquivo": "documento.pdf" (opcional)
    }
    
    Retorna o PDF como download ou erro.
    """
    try:
        logging.info("=== INICIO - Conversão Markdown para PDF ===")
        
        # Verifica se a requisição tem JSON
        if not request.is_json:
            return jsonify({
                "status": "erro",
                "mensagem": "Requisição deve conter JSON válido"
            }), 400
        
        data = request.get_json()
        
        # Valida se o texto markdown foi enviado
        if 'texto_markdown' not in data or not data['texto_markdown']:
            return jsonify({
                "status": "erro",
                "mensagem": "Campo 'texto_markdown' é obrigatório e não pode estar vazio"
            }), 400
        
        texto_markdown = data['texto_markdown']
        nome_arquivo = data.get('nome_arquivo', f'documento_{uuid.uuid4().hex[:8]}.pdf')
        
        # Garante que o arquivo tem extensão .pdf
        if not nome_arquivo.endswith('.pdf'):
            nome_arquivo += '.pdf'
        
        logging.info(f"Iniciando conversão para arquivo: {nome_arquivo}")
        logging.info(f"Tamanho do texto: {len(texto_markdown)} caracteres")
        
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
            
            return jsonify({
                "status": "erro",
                "mensagem": "Falha na conversão do Markdown para PDF"
            }), 500
        
        logging.info(f"Conversão realizada com sucesso: {nome_arquivo}")
        
        # Retorna o arquivo PDF como download
        def remove_file(response):
            try:
                os.unlink(temp_path)
            except Exception:
                pass
            return response
        
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=nome_arquivo,
            mimetype='application/pdf'
        ), 200
        
    except Exception as e:
        logging.error(f"Erro na conversão: {str(e)}")
        traceback.print_exc()
        
        # Remove arquivo temporário se houve erro
        try:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
        except Exception:
            pass
        
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro interno do servidor: {str(e)}"
        }), 500


@app.route("/converter-markdown-pdf-base64", methods=["POST"])
def converter_markdown_para_pdf_base64():
    """Converte texto Markdown para PDF e retorna em base64.
    
    Espera JSON com:
    {
        "texto_markdown": "# Título\nConteúdo...",
        "nome_arquivo": "documento.pdf" (opcional)
    }
    
    Retorna JSON com:
    {
        "status": "sucesso",
        "nome_arquivo": "documento.pdf",
        "pdf_base64": "base64_encoded_pdf_data",
        "tamanho": 1234
    }
    """
    try:
        logging.info("=== INICIO - Conversão Markdown para PDF (Base64) ===")
        
        # Verifica se a requisição tem JSON
        if not request.is_json:
            return jsonify({
                "status": "erro",
                "mensagem": "Requisição deve conter JSON válido"
            }), 400
        
        data = request.get_json()
        
        # Valida se o texto markdown foi enviado
        if 'texto_markdown' not in data or not data['texto_markdown']:
            return jsonify({
                "status": "erro",
                "mensagem": "Campo 'texto_markdown' é obrigatório e não pode estar vazio"
            }), 400
        
        texto_markdown = data['texto_markdown']
        nome_arquivo = data.get('nome_arquivo', f'documento_{uuid.uuid4().hex[:8]}.pdf')
        
        # Garante que o arquivo tem extensão .pdf
        if not nome_arquivo.endswith('.pdf'):
            nome_arquivo += '.pdf'
        
        logging.info(f"Iniciando conversão para arquivo: {nome_arquivo}")
        
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
            
            return jsonify({
                "status": "erro",
                "mensagem": "Falha na conversão do Markdown para PDF"
            }), 500
        
        # Lê o arquivo PDF e converte para base64
        import base64
        with open(temp_path, 'rb') as pdf_file:
            pdf_content = pdf_file.read()
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
        
        # Remove arquivo temporário
        os.unlink(temp_path)
        
        logging.info(f"Conversão realizada com sucesso: {nome_arquivo} ({len(pdf_content)} bytes)")
        
        return jsonify({
            "status": "sucesso",
            "nome_arquivo": nome_arquivo,
            "pdf_base64": pdf_base64,
            "tamanho": len(pdf_content)
        }), 200
        
    except Exception as e:
        logging.error(f"Erro na conversão: {str(e)}")
        traceback.print_exc()
        
        # Remove arquivo temporário se houve erro
        try:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
        except Exception:
            pass
        
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro interno do servidor: {str(e)}"
        }), 500


@app.route("/converter-markdown-docx", methods=["POST"])
def converter_markdown_para_docx_api():
    """Converte texto Markdown para Word (.docx) via API.
    
    Espera JSON com:
    {
        "texto_markdown": "# Título\nConteúdo...",
        "nome_arquivo": "documento.docx" (opcional)
    }
    
    Retorna o documento Word como download ou erro.
    """
    try:
        logging.info("=== INICIO - Conversão Markdown para Word ===")
        
        # Verifica se a requisição tem JSON
        if not request.is_json:
            return jsonify({
                "status": "erro",
                "mensagem": "Requisição deve conter JSON válido"
            }), 400
        
        data = request.get_json()
        
        # Valida se o texto markdown foi enviado
        if 'texto_markdown' not in data or not data['texto_markdown']:
            return jsonify({
                "status": "erro",
                "mensagem": "Campo 'texto_markdown' é obrigatório e não pode estar vazio"
            }), 400
        
        texto_markdown = data['texto_markdown']
        nome_arquivo = data.get('nome_arquivo', f'documento_{uuid.uuid4().hex[:8]}.docx')
        
        # Garante que o arquivo tem extensão .docx
        if not nome_arquivo.endswith('.docx'):
            nome_arquivo += '.docx'
        
        logging.info(f"Iniciando conversão para arquivo: {nome_arquivo}")
        logging.info(f"Tamanho do texto: {len(texto_markdown)} caracteres")
        
        # Cria arquivo temporário para o Word
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
            temp_path = temp_file.name
        
        # Converte o Markdown para Word
        converter = MarkdownToDocx()
        sucesso = converter.markdown_text_to_docx(texto_markdown, temp_path)
        
        if not sucesso:
            # Remove arquivo temporário se falhou
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            
            return jsonify({
                "status": "erro",
                "mensagem": "Falha na conversão do Markdown para Word"
            }), 500
        
        logging.info(f"Conversão realizada com sucesso: {nome_arquivo}")
        
        # Retorna o arquivo Word como download
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=nome_arquivo,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ), 200
        
    except Exception as e:
        logging.error(f"Erro na conversão: {str(e)}")
        traceback.print_exc()
        
        # Remove arquivo temporário se houve erro
        try:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
        except Exception:
            pass
        
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro interno do servidor: {str(e)}"
        }), 500


@app.route("/converter-markdown-docx-base64", methods=["POST"])
def converter_markdown_para_docx_base64():
    """Converte texto Markdown para Word e retorna em base64.
    
    Espera JSON com:
    {
        "texto_markdown": "# Título\nConteúdo...",
        "nome_arquivo": "documento.docx" (opcional)
    }
    
    Retorna JSON com:
    {
        "status": "sucesso",
        "nome_arquivo": "documento.docx",
        "docx_base64": "base64_encoded_docx_data",
        "tamanho": 1234
    }
    """
    try:
        logging.info("=== INICIO - Conversão Markdown para Word (Base64) ===")
        
        # Verifica se a requisição tem JSON
        if not request.is_json:
            return jsonify({
                "status": "erro",
                "mensagem": "Requisição deve conter JSON válido"
            }), 400
        
        data = request.get_json()
        
        # Valida se o texto markdown foi enviado
        if 'texto_markdown' not in data or not data['texto_markdown']:
            return jsonify({
                "status": "erro",
                "mensagem": "Campo 'texto_markdown' é obrigatório e não pode estar vazio"
            }), 400
        
        texto_markdown = data['texto_markdown']
        nome_arquivo = data.get('nome_arquivo', f'documento_{uuid.uuid4().hex[:8]}.docx')
        
        # Garante que o arquivo tem extensão .docx
        if not nome_arquivo.endswith('.docx'):
            nome_arquivo += '.docx'
        
        logging.info(f"Iniciando conversão para arquivo: {nome_arquivo}")
        
        # Cria arquivo temporário para o Word
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
            temp_path = temp_file.name
        
        # Converte o Markdown para Word
        converter = MarkdownToDocx()
        sucesso = converter.markdown_text_to_docx(texto_markdown, temp_path)
        
        if not sucesso:
            # Remove arquivo temporário se falhou
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            
            return jsonify({
                "status": "erro",
                "mensagem": "Falha na conversão do Markdown para Word"
            }), 500
        
        # Lê o arquivo Word e converte para base64
        import base64
        with open(temp_path, 'rb') as docx_file:
            docx_content = docx_file.read()
            docx_base64 = base64.b64encode(docx_content).decode('utf-8')
        
        # Remove arquivo temporário
        os.unlink(temp_path)
        
        logging.info(f"Conversão realizada com sucesso: {nome_arquivo} ({len(docx_content)} bytes)")
        
        return jsonify({
            "status": "sucesso",
            "nome_arquivo": nome_arquivo,
            "docx_base64": docx_base64,
            "tamanho": len(docx_content)
        }), 200
        
    except Exception as e:
        logging.error(f"Erro na conversão: {str(e)}")
        traceback.print_exc()
        
        # Remove arquivo temporário se houve erro
        try:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
        except Exception:
            pass
        
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro interno do servidor: {str(e)}"
        }), 500


# Inicia o servidor Flask escutando em todas interfaces, porta 8000
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)