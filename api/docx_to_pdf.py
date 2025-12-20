"""
Módulo para conversão de arquivos DOC/DOCX para PDF usando python-docx e reportlab
Versão para API Vercel
"""

import os
import tempfile
import logging
from docx import Document
from docx.shared import Inches
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY


class DocxToPdf:
    def __init__(self):
        """Inicializa o conversor DOCX para PDF"""
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configura estilos personalizados para o PDF"""
        # Estilo para título
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            spaceAfter=12,
            textColor=colors.black,
            alignment=TA_CENTER
        ))
        
        # Estilo para subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            textColor=colors.black,
            alignment=TA_LEFT
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=colors.black,
            alignment=TA_JUSTIFY
        ))
    
    def _escape_special_chars(self, text):
        """Escapa caracteres especiais para ReportLab"""
        if not text:
            return ""
        
        # Garante que é uma string
        if not isinstance(text, str):
            text = str(text)
        
        # Escapa caracteres XML/HTML
        import html
        escaped = html.escape(text)
        
        # Remove ou substitui caracteres problemáticos
        escaped = escaped.replace('\x91', "'")  # Apostrofe curvo esquerdo
        escaped = escaped.replace('\x92', "'")  # Apostrofe curvo direito  
        escaped = escaped.replace('\x93', '"')  # Aspas curvas esquerdas
        escaped = escaped.replace('\x94', '"')  # Aspas curvas direitas
        escaped = escaped.replace('\x96', '-')  # Hífen longo
        escaped = escaped.replace('\x97', '--') # Hífen extra longo
        
        return escaped
    
    def extract_text_from_docx(self, docx_path):
        """Extrai texto de um arquivo DOCX"""
        try:
            # Verifica se o arquivo existe e é válido
            if not os.path.exists(docx_path):
                logging.error(f"Arquivo não encontrado: {docx_path}")
                return None
                
            # Tenta abrir o documento
            try:
                doc = Document(docx_path)
            except Exception as e:
                logging.error(f"Erro ao abrir documento DOCX: {str(e)}")
                return None
                
            text_content = []
            
            # Adiciona conteúdo padrão se documento estiver vazio
            if not doc.paragraphs and not doc.tables:
                text_content.append(('normal', 'Documento convertido de DOCX'))
                return text_content
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    # Limpa o texto para evitar problemas de encoding
                    clean_text = paragraph.text.encode('utf-8', errors='ignore').decode('utf-8')
                    
                    # Verifica o estilo do parágrafo para determinar formatação
                    style_name = paragraph.style.name.lower()
                    
                    if 'title' in style_name:
                        text_content.append(('title', clean_text))
                    elif 'heading' in style_name:
                        text_content.append(('heading', clean_text))
                    else:
                        text_content.append(('normal', clean_text))
            
            # Processa tabelas se existirem
            for table in doc.tables:
                table_data = []
                for row in table.rows:
                    row_data = []
                    for cell in row.cells:
                        # Limpa o texto da célula
                        clean_cell_text = cell.text.strip().encode('utf-8', errors='ignore').decode('utf-8')
                        row_data.append(clean_cell_text)
                    table_data.append(row_data)
                if table_data:
                    text_content.append(('table', table_data))
                    
            return text_content
            
        except Exception as e:
            logging.error(f"Erro ao extrair texto do DOCX: {str(e)}")
            return None
    
    def create_pdf_from_content(self, content, pdf_path):
        """Cria um PDF a partir do conteúdo extraído"""
        try:
            doc = SimpleDocTemplate(pdf_path, pagesize=A4, 
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            
            story = []
            
            for content_type, data in content:
                if content_type == 'title':
                    # Escapa caracteres especiais para ReportLab
                    safe_text = self._escape_special_chars(data)
                    story.append(Paragraph(safe_text, self.styles['CustomTitle']))
                    story.append(Spacer(1, 12))
                    
                elif content_type == 'heading':
                    safe_text = self._escape_special_chars(data)
                    story.append(Paragraph(safe_text, self.styles['CustomHeading']))
                    story.append(Spacer(1, 6))
                    
                elif content_type == 'normal':
                    safe_text = self._escape_special_chars(data)
                    story.append(Paragraph(safe_text, self.styles['CustomNormal']))
                    story.append(Spacer(1, 6))
                    
                elif content_type == 'table':
                    # Cria tabela no PDF
                    if data and len(data) > 0:
                        # Processa dados da tabela para escapar caracteres especiais
                        safe_table_data = []
                        for row in data:
                            safe_row = [self._escape_special_chars(cell) for cell in row]
                            safe_table_data.append(safe_row)
                            
                        table = Table(safe_table_data)
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 10),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 1), (-1, -1), 9),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ]))
                        story.append(table)
                        story.append(Spacer(1, 12))
            
            # Constrói o PDF
            doc.build(story)
            return True
            
        except Exception as e:
            logging.error(f"Erro ao criar PDF: {str(e)}")
            return False
    
    def convert_docx_to_pdf(self, docx_path, pdf_path):
        """Converte um arquivo DOCX para PDF"""
        try:
            logging.info(f"Iniciando conversão: {docx_path} -> {pdf_path}")
            
            # Verifica se o arquivo DOCX existe
            if not os.path.exists(docx_path):
                logging.error(f"Arquivo DOCX não encontrado: {docx_path}")
                return False
            
            # Extrai conteúdo do DOCX
            content = self.extract_text_from_docx(docx_path)
            if not content:
                logging.error("Falha ao extrair conteúdo do DOCX")
                return False
            
            # Cria o PDF
            success = self.create_pdf_from_content(content, pdf_path)
            
            if success:
                logging.info(f"Conversão realizada com sucesso: {pdf_path}")
                return True
            else:
                logging.error("Falha ao criar PDF")
                return False
                
        except Exception as e:
            logging.error(f"Erro geral na conversão: {str(e)}")
            return False
    
    def convert_docx_content_to_pdf(self, docx_file_content, pdf_path):
        """Converte conteúdo de arquivo DOCX (bytes) para PDF"""
        try:
            # Cria arquivo temporário para o DOCX
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_docx:
                temp_docx.write(docx_file_content)
                temp_docx_path = temp_docx.name
            
            # Converte para PDF
            result = self.convert_docx_to_pdf(temp_docx_path, pdf_path)
            
            # Remove arquivo temporário
            try:
                os.unlink(temp_docx_path)
            except Exception:
                pass
            
            return result
            
        except Exception as e:
            logging.error(f"Erro na conversão de conteúdo DOCX: {str(e)}")
            return False


def main():
    """Função principal para testes"""
    converter = DocxToPdf()
    
    # Exemplo de uso
    docx_file = "exemplo.docx"
    pdf_file = "exemplo.pdf"
    
    if converter.convert_docx_to_pdf(docx_file, pdf_file):
        print(f"Conversão realizada com sucesso: {pdf_file}")
    else:
        print("Falha na conversão")


if __name__ == "__main__":
    main()