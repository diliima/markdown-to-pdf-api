# Conversor Markdown para PDF + DOCX para PDF

Este projeto oferece uma solução simples e eficaz para converter textos Markdown em PDF/Word e converter arquivos DOCX/DOC em PDF usando Python.

## 🚀 Características

- ✅ **Compatível com Windows** - Não requer dependências externas complexas
- ✅ **Múltiplos formatos** - Markdown para PDF/Word, DOCX/DOC para PDF  
- ✅ **API REST** - Interface HTTP para integração com outros sistemas
- ✅ **Fácil de usar** - Interface simples e intuitiva
- ✅ **Rápido** - Conversão eficiente usando ReportLab e python-docx
- ✅ **Flexível** - Suporta texto direto ou arquivos
- ✅ **Bem formatado** - PDFs com estilos profissionais

## 📦 Dependências

As seguintes bibliotecas são necessárias (já instaladas no ambiente):

```
flask
reportlab
markdown2
python-docx
pandas
openpyxl
```

## 🛠️ Como Usar

### Método 1: Importando no seu código

```python
from conversor_md_pdf import converter_markdown_para_pdf

# Converter texto Markdown diretamente
texto_markdown = """
# Meu Relatório

## Introdução

Este é um exemplo de **texto importante** em *itálico*.

### Lista de itens:

- Item 1
- Item 2 
- Item 3

```python
def exemplo():
    print("Código de exemplo")
```

> Esta é uma citação importante.

## Conclusão

Relatório finalizado com **sucesso**!
"""

# Gerar PDF
sucesso = converter_markdown_para_pdf(texto_markdown, "meu_relatorio.pdf")

if sucesso:
    print("PDF criado com sucesso!")
```

### Método 2: Convertendo arquivos .md

```python
from conversor_md_pdf import converter_arquivo_md_para_pdf

# Converter arquivo Markdown para PDF
converter_arquivo_md_para_pdf("README.md", "README.pdf")

# Ou deixar o nome automático (README.md → README.pdf)
converter_arquivo_md_para_pdf("README.md")
```

### Método 3: Via linha de comando

```bash
# Ativar ambiente virtual
env\Scripts\activate

# Converter arquivo específico
python markdown_to_pdf_reportlab.py documento.md -o saida.pdf

# Conversão automática (mesmo nome)
python markdown_to_pdf_reportlab.py documento.md
```

## 🎨 Elementos Suportados

O conversor suporta os seguintes elementos Markdown:

| Elemento | Markdown | Resultado |
|----------|----------|-----------|
| **Título 1** | `# Título` | Título grande e destacado |
| **Título 2** | `## Subtítulo` | Subtítulo médio |
| **Título 3** | `### Subsubtítulo` | Subtítulo pequeno |
| **Negrito** | `**texto**` | **Texto em negrito** |
| **Itálico** | `*texto*` | *Texto em itálico* |
| **Código inline** | `` `código` `` | `código formatado` |
| **Bloco de código** | ``` ```código``` ``` | Bloco destacado |
| **Lista** | `- item` | • Lista com marcadores |
| **Lista numerada** | `1. item` | 1. Lista numerada |
| **Citação** | `> texto` | Bloco de citação |

## 📁 Arquivos do Projeto

- `markdown_to_pdf_reportlab.py` - Conversor principal (completo)
- `conversor_md_pdf.py` - Interface simplificada para uso
- `exemplo_uso.md` - Exemplos de como usar
- `demo.pdf` - Arquivo de demonstração gerado

## 🔧 Personalização

Para customizar estilos, você pode modificar a classe `MarkdownToPDFReportLab` no arquivo principal:

```python
# Exemplo de customização
from markdown_to_pdf_reportlab import MarkdownToPDFReportLab
from reportlab.lib.pagesizes import letter

# Criar conversor com página Letter (ao invés de A4)
conversor = MarkdownToPDFReportLab(page_size=letter)

# Usar conversor customizado
conversor.markdown_text_to_pdf(texto, "saida.pdf")
```

### Método 3: Converter DOCX/DOC para PDF

```python
from docx_to_pdf import DocxToPdf

# Converter arquivo DOCX para PDF
converter = DocxToPdf()
sucesso = converter.convert_docx_to_pdf("documento.docx", "documento.pdf")

if sucesso:
    print("Conversão realizada com sucesso!")
else:
    print("Falha na conversão")
```

### Método 4: API REST

O projeto inclui uma API Flask completa:

```bash
# Iniciar o servidor
python app.py
```

**Endpoints disponíveis:**

- `GET /verificar` - Health check
- `POST /converter-markdown-pdf` - Markdown para PDF (download)
- `POST /converter-markdown-pdf-base64` - Markdown para PDF (base64)
- `POST /converter-markdown-docx` - Markdown para DOCX (download)
- `POST /converter-markdown-docx-base64` - Markdown para DOCX (base64)
- `POST /converter-docx-pdf` - DOCX/DOC para PDF (download)
- `POST /converter-docx-pdf-base64` - DOCX/DOC para PDF (base64)
- `POST /converter-json-excel-base64` - JSON para Excel (base64)

**Exemplo de uso da API:**

```python
import requests

# Converter Markdown para PDF
response = requests.post(
    'http://localhost:9000/converter-markdown-pdf-base64',
    json={
        'texto_markdown': '# Título\n\nConteúdo **formatado**.',
        'nome_arquivo': 'teste.pdf'
    }
)

# Converter DOCX para PDF
with open('documento.docx', 'rb') as file:
    response = requests.post(
        'http://localhost:9000/converter-docx-pdf',
        files={'arquivo': file},
        data={'nome_arquivo': 'convertido.pdf'}
    )
```

Consulte [API_DOCS.md](API_DOCS.md) para documentação completa.

## 🧪 Teste Rápido

Execute o exemplo de demonstração:

```bash
python conversor_md_pdf.py
```

Isso criará um arquivo `demo.pdf` com exemplo de todas as funcionalidades.

## ❓ Solução de Problemas

### Erro de dependências no Windows

Se você tiver problemas com WeasyPrint no Windows, este projeto já usa ReportLab como alternativa, que é totalmente compatível.

### Encoding de caracteres

Certifique-se de que seus arquivos .md estão salvos em UTF-8 para suporte completo a caracteres especiais e acentos.

### Arquivos não encontrados

Sempre use caminhos absolutos ou certifique-se de estar no diretório correto ao executar os comandos.

## 🤝 Contribuindo

Sinta-se à vontade para melhorar o código, adicionar funcionalidades ou reportar problemas!

---

**Criado com ❤️ usando Python, ReportLab e Markdown2**