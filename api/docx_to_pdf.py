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
    
    def extract_text_from_docx(self, docx_path):
        """Extrai texto de um arquivo DOCX"""
        try:
            doc = Document(docx_path)
            text_content = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    # Verifica o estilo do parágrafo para determinar formatação
                    style_name = paragraph.style.name.lower()
                    
                    if 'title' in style_name:
                        text_content.append(('title', paragraph.text))
                    elif 'heading' in style_name:
                        text_content.append(('heading', paragraph.text))
                    else:
                        text_content.append(('normal', paragraph.text))
            
            # Processa tabelas se existirem
            for table in doc.tables:
                table_data = []
                for row in table.rows:
                    row_data = []
                    for cell in row.cells:
                        row_data.append(cell.text.strip())
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
                    story.append(Paragraph(data, self.styles['CustomTitle']))
                    story.append(Spacer(1, 12))
                    
                elif content_type == 'heading':
                    story.append(Paragraph(data, self.styles['CustomHeading']))
                    story.append(Spacer(1, 6))
                    
                elif content_type == 'normal':
                    story.append(Paragraph(data, self.styles['CustomNormal']))
                    story.append(Spacer(1, 6))
                    
                elif content_type == 'table':
                    # Cria tabela no PDF
                    if data and len(data) > 0:
                        table = Table(data)
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