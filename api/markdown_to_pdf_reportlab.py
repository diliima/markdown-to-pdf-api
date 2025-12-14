import markdown2
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, Image, Table, TableStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import re
import os
import argparse
import logging
from typing import Optional, List
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MarkdownToPDFReportLab:
    """
    Classe para converter arquivos Markdown para PDF usando ReportLab.
    Compatível com Windows e não requer dependências externas complexas.
    """
    
    def __init__(self, page_size=A4):
        """
        Inicializa o conversor.
        
        Args:
            page_size: Tamanho da página (A4, letter, etc.)
        """
        self.page_size = page_size
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """
        Configura estilos customizados para o PDF.
        """
        # Estilo para título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.HexColor('#34495e'),
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para heading 3
        self.styles.add(ParagraphStyle(
            name='CustomHeading3',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=15,
            textColor=colors.HexColor('#34495e'),
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            textColor=colors.black,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Estilo para código
        self.styles.add(ParagraphStyle(
            name='CustomCode',
            parent=self.styles['Code'],
            fontSize=9,
            spaceAfter=12,
            leftIndent=20,
            backgroundColor=colors.HexColor('#f8f9fa'),
            borderColor=colors.HexColor('#3498db'),
            borderWidth=1,
            borderPadding=8,
            fontName='Courier'
        ))
        
        # Estilo para citações
        self.styles.add(ParagraphStyle(
            name='CustomQuote',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=30,
            rightIndent=30,
            spaceAfter=12,
            fontName='Helvetica-Oblique',
            textColor=colors.HexColor('#5d6d7e'),
            borderColor=colors.HexColor('#3498db'),
            borderWidth=2,
            borderPadding=10
        ))
    
    def _parse_markdown_to_elements(self, markdown_text: str) -> List:
        """
        Converte texto Markdown em elementos ReportLab.
        
        Args:
            markdown_text (str): Texto em formato Markdown
            
        Returns:
            List: Lista de elementos ReportLab para construção do PDF
        """
        elements = []
        
        # Converte Markdown para HTML
        html = markdown2.markdown(
            markdown_text,
            extras=['fenced-code-blocks', 'tables', 'strike', 'task_list']
        )
        
        # Divide o HTML em linhas para processamento
        lines = html.split('\n')
        current_paragraph = []
        in_code_block = False
        in_blockquote = False
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                if current_paragraph:
                    elements.append(Paragraph(' '.join(current_paragraph), self.styles['CustomNormal']))
                    current_paragraph = []
                i += 1
                continue
            
            # Cabeçalhos
            if line.startswith('<h1>') and line.endswith('</h1>'):
                if current_paragraph:
                    elements.append(Paragraph(' '.join(current_paragraph), self.styles['CustomNormal']))
                    current_paragraph = []
                title = self._clean_html_tags(line)
                elements.append(Paragraph(title, self.styles['CustomTitle']))
                elements.append(Spacer(1, 12))
                
            elif line.startswith('<h2>') and line.endswith('</h2>'):
                if current_paragraph:
                    elements.append(Paragraph(' '.join(current_paragraph), self.styles['CustomNormal']))
                    current_paragraph = []
                title = self._clean_html_tags(line)
                elements.append(Paragraph(title, self.styles['CustomHeading2']))
                elements.append(Spacer(1, 8))
                
            elif line.startswith('<h3>') and line.endswith('</h3>'):
                if current_paragraph:
                    elements.append(Paragraph(' '.join(current_paragraph), self.styles['CustomNormal']))
                    current_paragraph = []
                title = self._clean_html_tags(line)
                elements.append(Paragraph(title, self.styles['CustomHeading3']))
                elements.append(Spacer(1, 6))
            
            # Bloco de código
            elif line.startswith('<pre><code>'):
                if current_paragraph:
                    elements.append(Paragraph(' '.join(current_paragraph), self.styles['CustomNormal']))
                    current_paragraph = []
                
                # Coleta todo o bloco de código
                code_lines = []
                if line.endswith('</code></pre>'):
                    # Código em uma linha
                    code_content = line.replace('<pre><code>', '').replace('</code></pre>', '')
                    elements.append(Preformatted(code_content, self.styles['CustomCode']))
                else:
                    # Código em múltiplas linhas
                    code_lines.append(line.replace('<pre><code>', ''))
                    i += 1
                    while i < len(lines) and not lines[i].strip().endswith('</code></pre>'):
                        code_lines.append(lines[i])
                        i += 1
                    if i < len(lines):
                        code_lines.append(lines[i].replace('</code></pre>', ''))
                    
                    code_content = '\n'.join(code_lines)
                    elements.append(Preformatted(code_content, self.styles['CustomCode']))
                elements.append(Spacer(1, 12))
                
            # Blockquote
            elif line.startswith('<blockquote>'):
                if current_paragraph:
                    elements.append(Paragraph(' '.join(current_paragraph), self.styles['CustomNormal']))
                    current_paragraph = []
                
                quote_lines = []
                if line.endswith('</blockquote>'):
                    quote_content = line.replace('<blockquote>', '').replace('</blockquote>', '')
                    elements.append(Paragraph(self._clean_html_tags(quote_content), self.styles['CustomQuote']))
                else:
                    quote_lines.append(line.replace('<blockquote>', ''))
                    i += 1
                    while i < len(lines) and not lines[i].strip().endswith('</blockquote>'):
                        quote_lines.append(lines[i])
                        i += 1
                    if i < len(lines):
                        quote_lines.append(lines[i].replace('</blockquote>', ''))
                    
                    quote_content = ' '.join(quote_lines)
                    elements.append(Paragraph(self._clean_html_tags(quote_content), self.styles['CustomQuote']))
                elements.append(Spacer(1, 12))
            
            # Lista
            elif line.startswith('<ul>') or line.startswith('<ol>'):
                if current_paragraph:
                    elements.append(Paragraph(' '.join(current_paragraph), self.styles['CustomNormal']))
                    current_paragraph = []
                
                # Processa lista
                list_items = []
                i += 1
                while i < len(lines) and not (lines[i].strip() == '</ul>' or lines[i].strip() == '</ol>'):
                    if lines[i].strip().startswith('<li>'):
                        item_text = self._clean_html_tags(lines[i].strip())
                        list_items.append(f"• {item_text}")
                    i += 1
                
                for item in list_items:
                    elements.append(Paragraph(item, self.styles['CustomNormal']))
                elements.append(Spacer(1, 8))
            
            # Parágrafo normal
            elif line.startswith('<p>') and line.endswith('</p>'):
                if current_paragraph:
                    elements.append(Paragraph(' '.join(current_paragraph), self.styles['CustomNormal']))
                    current_paragraph = []
                text = self._clean_html_tags(line)
                elements.append(Paragraph(text, self.styles['CustomNormal']))
                elements.append(Spacer(1, 6))
            
            # Código inline ou outros elementos
            else:
                current_paragraph.append(self._clean_html_tags(line))
            
            i += 1
        
        # Adiciona último parágrafo se existir
        if current_paragraph:
            elements.append(Paragraph(' '.join(current_paragraph), self.styles['CustomNormal']))
        
        return elements
    
    def _clean_html_tags(self, text: str) -> str:
        """
        Remove tags HTML e processa formatação básica.
        
        Args:
            text (str): Texto com tags HTML
            
        Returns:
            str: Texto limpo com formatação ReportLab
        """
        # Remove tags básicas
        text = re.sub(r'<p.*?>', '', text)
        text = re.sub(r'</p>', '', text)
        text = re.sub(r'<li.*?>', '', text)
        text = re.sub(r'</li>', '', text)
        text = re.sub(r'<ul.*?>', '', text)
        text = re.sub(r'</ul>', '', text)
        text = re.sub(r'<ol.*?>', '', text)
        text = re.sub(r'</ol>', '', text)
        text = re.sub(r'<h[1-6].*?>', '', text)
        text = re.sub(r'</h[1-6]>', '', text)
        text = re.sub(r'<blockquote.*?>', '', text)
        text = re.sub(r'</blockquote>', '', text)
        
        # Converte formatação para ReportLab
        text = re.sub(r'<strong>(.*?)</strong>', r'<b>\1</b>', text)
        text = re.sub(r'<em>(.*?)</em>', r'<i>\1</i>', text)
        text = re.sub(r'<code>(.*?)</code>', r'<font name="Courier" size="9">\1</font>', text)
        
        # Remove outras tags não suportadas
        text = re.sub(r'<[^>]+>', '', text)
        
        return text.strip()
    
    def markdown_text_to_pdf(self, markdown_text: str, output_path: str) -> bool:
        """
        Converte texto Markdown diretamente para PDF.
        
        Args:
            markdown_text (str): Texto em formato Markdown
            output_path (str): Caminho onde salvar o PDF gerado
            
        Returns:
            bool: True se a conversão foi bem-sucedida, False caso contrário
        """
        try:
            logger.info("Iniciando conversão de texto Markdown para PDF...")
            
            # Cria o documento PDF
            doc = SimpleDocTemplate(
                output_path,
                pagesize=self.page_size,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Converte Markdown em elementos
            elements = self._parse_markdown_to_elements(markdown_text)
            
            # Constrói o PDF
            doc.build(elements)
            
            logger.info(f"PDF gerado com sucesso: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao converter Markdown para PDF: {str(e)}")
            return False
    
    def markdown_file_to_pdf(self, markdown_file: str, output_path: Optional[str] = None) -> bool:
        """
        Converte arquivo Markdown para PDF.
        
        Args:
            markdown_file (str): Caminho para o arquivo Markdown
            output_path (str, optional): Caminho onde salvar o PDF
            
        Returns:
            bool: True se a conversão foi bem-sucedida, False caso contrário
        """
        try:
            # Verifica se o arquivo existe
            if not os.path.exists(markdown_file):
                logger.error(f"Arquivo Markdown não encontrado: {markdown_file}")
                return False
            
            # Define o caminho de saída se não fornecido
            if output_path is None:
                path = Path(markdown_file)
                output_path = str(path.with_suffix('.pdf'))
            
            # Lê o conteúdo do arquivo Markdown
            with open(markdown_file, 'r', encoding='utf-8') as file:
                markdown_text = file.read()
            
            logger.info(f"Convertendo arquivo: {markdown_file} -> {output_path}")
            
            # Converte o texto para PDF
            return self.markdown_text_to_pdf(markdown_text, output_path)
            
        except Exception as e:
            logger.error(f"Erro ao processar arquivo Markdown: {str(e)}")
            return False