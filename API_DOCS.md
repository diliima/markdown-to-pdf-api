# API de Conversão Markdown para PDF e Word

## 🚀 Visão Geral

Esta API Flask permite converter texto Markdown em arquivos PDF ou Word (.docx) através de requisições HTTP. Oferece duas modalidades de retorno: download direto ou dados em base64.

## 📡 Endpoints Disponíveis

### 1. Health Check
**GET** `/verificar`

Verifica se a API está funcionando.

**Resposta:**
```json
{
    "status": "ok"
}
```

### 2. Conversão PDF com Download
**POST** `/converter-markdown-pdf`

Converte Markdown para PDF e retorna o arquivo para download.

**Body (JSON):**
```json
{
    "texto_markdown": "# Título\n\nConteúdo do documento...",
    "nome_arquivo": "documento.pdf"  // opcional
}
```

**Resposta:** 
- **200**: Arquivo PDF para download
- **400**: Erro de validação
- **500**: Erro interno

### 3. Conversão PDF com Base64
**POST** `/converter-markdown-pdf-base64`

Converte Markdown para PDF e retorna os dados em base64.

**Body (JSON):**
```json
{
    "texto_markdown": "# Título\n\nConteúdo do documento...",
    "nome_arquivo": "documento.pdf"  // opcional
}
```

**Resposta (200):**
```json
{
    "status": "sucesso",
    "nome_arquivo": "documento.pdf",
    "pdf_base64": "JVBERi0xLjQKMSAwIG9iago8PAo...",
    "tamanho": 2048
}
```

### 4. Conversão Word com Download
**POST** `/converter-markdown-docx`

Converte Markdown para Word (.docx) e retorna o arquivo para download.

**Body (JSON):**
```json
{
    "texto_markdown": "# Título\n\nConteúdo do documento...",
    "nome_arquivo": "documento.docx"  // opcional
}
```

**Resposta:** 
- **200**: Arquivo Word para download
- **400**: Erro de validação
- **500**: Erro interno

### 5. Conversão Word com Base64
**POST** `/converter-markdown-docx-base64`

Converte Markdown para Word (.docx) e retorna os dados em base64.

**Body (JSON):**
```json
{
    "texto_markdown": "# Título\n\nConteúdo do documento...",
    "nome_arquivo": "documento.docx"  // opcional
}
```

**Resposta (200):**
```json
{
    "status": "sucesso",
    "nome_arquivo": "documento.docx",
    "docx_base64": "UEsDBBQABgAIAAAAIQD...",
    "tamanho": 4096
}
```

## 🛠️ Como Usar

### 1. Iniciar o Servidor

```bash
# Ativar ambiente virtual
env\Scripts\activate

# Instalar dependências (se necessário)
pip install -r requirements.txt

# Iniciar servidor
python app.py
```

O servidor estará disponível em: `http://localhost:9000`

### 2. Exemplo com Python (requests)

```python
import requests
import base64

# Texto markdown
texto = """
# Meu Relatório

## Introdução
Este é um documento **importante** com formatação *rica*.

### Lista de tarefas:
- Item 1
- Item 2
- Item 3

```python
print("Exemplo de código Python")
def hello_world():
    return "Hello, World!"
```

> Esta é uma citação importante que demonstra 
> como o texto pode ser destacado no documento.

## Conclusão
Documento gerado automaticamente via API.
"""

# === CONVERSÃO PARA PDF ===

# Opção 1: PDF - Download direto
response = requests.post(
    'http://localhost:9000/converter-markdown-pdf',
    json={
        'texto_markdown': texto,
        'nome_arquivo': 'relatorio.pdf'
    }
)

if response.status_code == 200:
    with open('relatorio.pdf', 'wb') as f:
        f.write(response.content)
    print("PDF salvo com sucesso!")

# Opção 2: PDF - Base64
response = requests.post(
    'http://localhost:9000/converter-markdown-pdf-base64',
    json={
        'texto_markdown': texto,
        'nome_arquivo': 'relatorio.pdf'
    }
)

if response.status_code == 200:
    data = response.json()
    pdf_bytes = base64.b64decode(data['pdf_base64'])
    
    with open('relatorio_base64.pdf', 'wb') as f:
        f.write(pdf_bytes)
    print(f"PDF salvo: {data['nome_arquivo']} ({data['tamanho']} bytes)")

# === CONVERSÃO PARA WORD ===

# Opção 3: Word - Download direto
response = requests.post(
    'http://localhost:9000/converter-markdown-docx',
    json={
        'texto_markdown': texto,
        'nome_arquivo': 'relatorio.docx'
    }
)

if response.status_code == 200:
    with open('relatorio.docx', 'wb') as f:
        f.write(response.content)
    print("Word salvo com sucesso!")

# Opção 4: Word - Base64
response = requests.post(
    'http://localhost:9000/converter-markdown-docx-base64',
    json={
        'texto_markdown': texto,
        'nome_arquivo': 'relatorio.docx'
    }
)

if response.status_code == 200:
    data = response.json()
    docx_bytes = base64.b64decode(data['docx_base64'])
    
    with open('relatorio_base64.docx', 'wb') as f:
        f.write(docx_bytes)
    print(f"Word salvo: {data['nome_arquivo']} ({data['tamanho']} bytes)")
```

### 3. Exemplo com curl

```bash
# PDF - Download direto
curl -X POST http://localhost:9000/converter-markdown-pdf \
  -H "Content-Type: application/json" \
  -d '{"texto_markdown":"# Título\n\nConteúdo **formatado**.","nome_arquivo":"teste.pdf"}' \
  --output teste.pdf

# Word - Download direto
curl -X POST http://localhost:9000/converter-markdown-docx \
  -H "Content-Type: application/json" \
  -d '{"texto_markdown":"# Título\n\nConteúdo **formatado**.","nome_arquivo":"teste.docx"}' \
  --output teste.docx

# PDF - Base64
curl -X POST http://localhost:9000/converter-markdown-pdf-base64 \
  -H "Content-Type: application/json" \
  -d '{"texto_markdown":"# Título\n\nConteúdo **formatado**.","nome_arquivo":"teste.pdf"}'

# Word - Base64
curl -X POST http://localhost:9000/converter-markdown-docx-base64 \
  -H "Content-Type: application/json" \
  -d '{"texto_markdown":"# Título\n\nConteúdo **formatado**.","nome_arquivo":"teste.docx"}'

# Health check
curl http://localhost:9000/verificar
```

### 4. Exemplo com JavaScript (fetch)

```javascript
// Função genérica para converter Markdown
async function converterMarkdown(textoMarkdown, nomeArquivo, formato = 'pdf') {
    const endpoint = formato === 'pdf' ? 
        'converter-markdown-pdf-base64' : 
        'converter-markdown-docx-base64';
    
    const mimeType = formato === 'pdf' ? 
        'application/pdf' : 
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document';

    try {
        const response = await fetch(`http://localhost:9000/${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                texto_markdown: textoMarkdown,
                nome_arquivo: nomeArquivo
            })
        });

        if (response.ok) {
            const data = await response.json();
            const base64Key = formato === 'pdf' ? 'pdf_base64' : 'docx_base64';
            
            // Converter base64 para blob
            const byteCharacters = atob(data[base64Key]);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], { type: mimeType });

            // Criar link para download
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = data.nome_arquivo;
            link.click();
            
            console.log(`${formato.toUpperCase()} baixado com sucesso!`);
        } else {
            console.error('Erro na conversão:', response.statusText);
        }
    } catch (error) {
        console.error('Erro na requisição:', error);
    }
}

// Uso - Gerar PDF
const markdown = `
# Documento Web
## Gerado via JavaScript

Este documento foi criado a partir de uma **requisição web**.

### Funcionalidades:
- Conversão para PDF
- Conversão para Word
- Download automático

> Tecnologia moderna para processamento de documentos.
`;

converterMarkdown(markdown, 'documento_web.pdf', 'pdf');
converterMarkdown(markdown, 'documento_web.docx', 'docx');
```

## ⚡ Formatos Suportados

A API suporta os seguintes elementos Markdown em ambos PDF e Word:

| Elemento | Sintaxe | Exemplo | PDF | Word |
|----------|---------|---------|-----|------|
| Título 1 | `# Texto` | # Título Principal | ✅ | ✅ |
| Título 2 | `## Texto` | ## Subtítulo | ✅ | ✅ |
| Título 3 | `### Texto` | ### Subsubtítulo | ✅ | ✅ |
| Negrito | `**texto**` | **texto em negrito** | ✅ | ✅ |
| Itálico | `*texto*` | *texto em itálico* | ✅ | ✅ |
| Código inline | `` `código` `` | `print("hello")` | ✅ | ✅ |
| Bloco de código | ``` ```código``` ``` | Bloco destacado | ✅ | ✅ |
| Lista | `- item` | • Item da lista | ✅ | ✅ |
| Lista numerada | `1. item` | 1. Item numerado | ✅ | ✅ |
| Citação | `> texto` | Bloco de citação | ✅ | ✅ |

## ❗ Tratamento de Erros

### Códigos de Status HTTP

- **200**: Conversão realizada com sucesso
- **400**: Erro de validação (texto vazio, JSON inválido)
- **500**: Erro interno do servidor

### Exemplos de Erro

```json
// Texto vazio
{
    "status": "erro",
    "mensagem": "Campo 'texto_markdown' é obrigatório e não pode estar vazio"
}

// JSON inválido
{
    "status": "erro",
    "mensagem": "Requisição deve conter JSON válido"
}

// Erro interno
{
    "status": "erro",
    "mensagem": "Erro interno do servidor: ..."
}
```

## 📊 Comparação PDF vs Word

| Aspecto | PDF | Word (.docx) |
|---------|-----|-------------|
| Fidelidade visual | ✅ Alta | ⚠️ Dependente do software |
| Editabilidade | ❌ Limitada | ✅ Totalmente editável |
| Tamanho do arquivo | 🔸 Médio | 🔹 Pequeno |
| Compatibilidade | ✅ Universal | ✅ Ampla |
| Formatação complexa | ✅ Excelente | ✅ Boa |
| Uso recomendado | Documentos finais | Documentos de trabalho |

## 🔐 Considerações de Segurança

- A API não faz autenticação por padrão
- Arquivos temporários são automaticamente removidos
- Limite de tamanho do texto pode ser configurado no Flask
- Para produção, considere adicionar rate limiting

## 📊 Performance

- Conversões PDF típicas: 50-500ms
- Conversões Word típicas: 100-800ms
- Tamanho máximo recomendado: 10MB de texto
- Arquivos temporários são limpos automaticamente
- Suporte a requisições concorrentes

## 🐛 Resolução de Problemas

### Servidor não inicia
```bash
# Verificar se a porta está livre
netstat -an | findstr 9000

# Verificar dependências
pip list | findstr -i "flask reportlab markdown python-docx"
```

### Erro de conversão
- Verificar se o texto Markdown está válido
- Verificar logs do servidor
- Testar com texto simples primeiro

### Problemas de encoding
- Garantir que o texto está em UTF-8
- Verificar caracteres especiais no Markdown

### Dependências em falta
```bash
# Instalar todas as dependências
pip install flask reportlab markdown2 python-docx

# Ou usar o requirements.txt
pip install -r requirements.txt
```

---

**Pronto para usar! 🎉**

Agora você pode converter Markdown tanto para PDF quanto para Word através da mesma API!