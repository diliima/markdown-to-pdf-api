"""
Módulo robusto para conversão DOCX -> PDF.
Correções: Ordem cronológica de elementos (XML), Suporte a Fontes TTF e tratamento de erros granulares.
"""

import os
import tempfile
import logging
import html
from docx import Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.text.paragraph import Paragraph as DocxParagraph
from docx.table import Table as DocxTable

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class DocxToPdf:
    def __init__(self):
        """Inicializa o conversor e tenta carregar fontes melhores"""
        self.font_name = 'Helvetica' # Fallback padrão
        self._register_system_fonts()
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()

    def _register_system_fonts(self):
        """
        Tenta registrar uma fonte TTF (Arial, Verdana ou DejaVu) para suportar acentos corretamente.
        Em ambientes Docker/Linux, fontes Microsoft nem sempre estão presentes.
        """
        font_candidates = [
            ("Arial", "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf"),
            ("Arial", "/usr/share/fonts/truetype/arial.ttf"),
            ("DejaVuSans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ("Verdana", "/usr/share/fonts/truetype/verdana.ttf"),
            # Caminho comum no Windows para testes locais
            ("Arial", "C:\\Windows\\Fonts\\arial.ttf"), 
        ]

        for name, path in font_candidates:
            if os.path.exists(path):
                try:
                    pdfmetrics.registerFont(TTFont(name, path))
                    self.font_name = name
                    logging.info(f"Fonte registrada com sucesso: {name}")
                    return
                except Exception as e:
                    logging.warning(f"Erro ao registrar fonte {name}: {e}")
        
        logging.warning("Nenhuma fonte TTF encontrada. Usando Helvetica (pode ter problemas com acentos).")

    def setup_custom_styles(self):
        """Configura estilos usando a fonte registrada"""
        # Estilo Base
        base_style = {
            'fontName': self.font_name,
            'textColor': colors.black,
            'allowWidows': 0,
            'allowOrphans': 0,
        }

        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=12,
            **base_style
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=14,
            leading=18,
            alignment=TA_LEFT,
            spaceBefore=12,
            spaceAfter=6,
            **base_style
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
            **base_style
        ))

    def _process_text_run(self, paragraph):
        """Processa texto mantendo negrito/itálico"""
        text_parts = []
        if not paragraph.runs:
            return html.escape(paragraph.text)

        for run in paragraph.runs:
            # Limpa caracteres nulos ou inválidos
            text = run.text.replace('\x00', '')
            if not text:
                continue
            
            safe_text = html.escape(text)
            
            # Aplica formatação se a fonte permitir (Helvetica tem variantes, TTF precisa de registro específico)
            # Simplificação: Usamos tags <b> e <i> que o ReportLab tenta emular ou mapear
            if run.bold:
                safe_text = f"<b>{safe_text}</b>"
            if run.italic:
                safe_text = f"<i>{safe_text}</i>"
            if run.underline:
                safe_text = f"<u>{safe_text}</u>"
                
            text_parts.append(safe_text)
            
        return "".join(text_parts)

    def iter_block_items(self, parent):
        """
        Gera uma iteração sequencial de parágrafos e tabelas.
        Essa é a mágica para manter a ordem correta.
        """
        if isinstance(parent, Document):
            parent_elm = parent.element.body
        elif isinstance(parent, DocxTable): # Se quisermos processar células complexas no futuro
            parent_elm = parent._element
        else:
            raise ValueError("Objeto pai desconhecido")

        for child in parent_elm.iter_child_elements():
            if isinstance(child, CT_P):
                yield DocxParagraph(child, parent)
            elif isinstance(child, CT_Tbl):
                yield DocxTable(child, parent)

    def extract_ordered_content(self, docx_path):
        """Extrai conteúdo mantendo a ordem exata do documento"""
        try:
            doc = Document(docx_path)
            story_content = []

            # Itera sobre os elementos na ordem que aparecem no XML
            for block in self.iter_block_items(doc):
                
                # --- PROCESSAMENTO DE PARÁGRAFO ---
                if isinstance(block, DocxParagraph):
                    if not block.text.strip():
                        continue
                    
                    text_fmt = self._process_text_run(block)
                    style_name = block.style.name.lower()
                    
                    # Definição simples de estilo
                    if 'title' in style_name:
                        story_content.append(('title', text_fmt))
                    elif 'heading' in style_name:
                        story_content.append(('heading', text_fmt))
                    elif 'list' in style_name or 'bullet' in style_name:
                        # Adiciona o bullet manualmente
                        story_content.append(('list_bullet', text_fmt))
                    else:
                        story_content.append(('normal', text_fmt))

                # --- PROCESSAMENTO DE TABELA ---
                elif isinstance(block, DocxTable):
                    table_data = []
                    for row in block.rows:
                        row_data = []
                        for cell in row.cells:
                            # Converte texto da célula em Parágrafo do ReportLab para permitir quebra de linha
                            cell_text = cell.text.strip()
                            if cell_text:
                                p = Paragraph(html.escape(cell_text), self.styles['Normal']) # Usa estilo padrão aqui para caber
                                row_data.append(p)
                            else:
                                row_data.append("")
                        table_data.append(row_data)
                    
                    if table_data:
                        story_content.append(('table', table_data))

            return story_content

        except Exception as e:
            logging.error(f"Erro na extração ordenada: {e}")
            raise e # Repassa o erro para ser capturado no handler principal

    def create_pdf(self, content, output_path):
        """Gera o PDF final"""
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=50, leftMargin=50,
                topMargin=50, bottomMargin=50
            )
            
            story = []
            
            for kind, data in content:
                # Adiciona cada elemento ao 'Story' do ReportLab
                if kind == 'title':
                    story.append(Paragraph(data, self.styles['CustomTitle']))
                    story.append(Spacer(1, 12))
                
                elif kind == 'heading':
                    story.append(Paragraph(data, self.styles['CustomHeading']))
                    story.append(Spacer(1, 6))
                
                elif kind == 'normal':
                    story.append(Paragraph(data, self.styles['CustomNormal']))
                    story.append(Spacer(1, 6))
                
                elif kind == 'list_bullet':
                    # Simula lista com indentação
                    p = Paragraph(f"• {data}", self.styles['CustomNormal'])
                    # Ajuste fino de indentação poderia ser feito aqui com ListFlowable, mas Paragraph resolve
                    story.append(p)
                    story.append(Spacer(1, 4))

                elif kind == 'table':
                    if len(data) > 0:
                        # Estilo da Tabela
                        tbl = Table(data)
                        tbl.setStyle(TableStyle([
                            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                            ('VALIGN', (0,0), (-1,-1), 'TOP'),
                            ('FONTNAME', (0,0), (-1,-1), self.font_name),
                            ('FONTSIZE', (0,0), (-1,-1), 9),
                            ('PADDING', (0,0), (-1,-1), 4),
                        ]))
                        # Ajusta largura automaticamente para caber na página (A4 width ~595 pts - margens)
                        # tbl._argW[n] pode ser usado se precisar fixar colunas
                        story.append(tbl)
                        story.append(Spacer(1, 12))

            doc.build(story)
            return True

        except Exception as e:
            logging.error(f"Erro na construção do PDF: {e}")
            return False

    def convert_docx_content_to_pdf(self, docx_bytes, pdf_path):
        """Método público principal"""
        temp_input = None
        try:
            # Salva bytes em arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
                tmp.write(docx_bytes)
                temp_input = tmp.name
            
            # 1. Extrai conteúdo na ordem correta
            content = self.extract_ordered_content(temp_input)
            
            # 2. Gera PDF
            success = self.create_pdf(content, pdf_path)
            
            return success

        except Exception as e:
            logging.error(f"Erro fatal na conversão: {e}")
            return False
        finally:
            if temp_input and os.path.exists(temp_input):
                try: os.unlink(temp_input) 
                except: pass