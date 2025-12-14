# API de Conversão Markdown para PDF

## 🚀 Visão Geral

Esta API Flask permite converter texto Markdown em arquivos PDF através de requisições HTTP. Oferece duas modalidades de retorno: download direto ou dados em base64.

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

### 2. Conversão com Download
**POST** `/converter-markdown-pdf`

Converte Markdown para PDF e retorna o arquivo para download.

**Body (JSON):**
```json
{
    "texto_markdown": "# Título\n\nConte**údo** do documento...",
    "nome_arquivo": "documento.pdf"  // opcional
}
```

**Resposta:** 
- **200**: Arquivo PDF para download
- **400**: Erro de validação
- **500**: Erro interno

### 3. Conversão com Base64
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

## 🛠️ Como Usar

### 1. Iniciar o Servidor

```bash
# Ativar ambiente virtual
env\Scripts\activate

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
Este é um documento **importante**.

### Lista:
- Item 1
- Item 2
- Item 3

```python
print("Exemplo de código")
```

> Citação importante.
"""

# Opção 1: Download direto
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

# Opção 2: Base64
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
```

### 3. Exemplo com curl

```bash
# Download direto
curl -X POST http://localhost:9000/converter-markdown-pdf \
  -H "Content-Type: application/json" \
  -d '{"texto_markdown":"# Título\n\nConteúdo **formatado**.","nome_arquivo":"teste.pdf"}' \
  --output teste.pdf

# Base64
curl -X POST http://localhost:9000/converter-markdown-pdf-base64 \
  -H "Content-Type: application/json" \
  -d '{"texto_markdown":"# Título\n\nConteúdo **formatado**.","nome_arquivo":"teste.pdf"}'

# Health check
curl http://localhost:9000/verificar
```

### 4. Exemplo com JavaScript (fetch)

```javascript
// Função para converter Markdown para PDF
async function converterMarkdownPDF(textoMarkdown, nomeArquivo) {
    try {
        const response = await fetch('http://localhost:9000/converter-markdown-pdf-base64', {
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
            
            // Converter base64 para blob
            const byteCharacters = atob(data.pdf_base64);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], { type: 'application/pdf' });

            // Criar link para download
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = data.nome_arquivo;
            link.click();
            
            console.log('PDF baixado com sucesso!');
        } else {
            console.error('Erro na conversão:', response.statusText);
        }
    } catch (error) {
        console.error('Erro na requisição:', error);
    }
}

// Uso
const markdown = `
# Documento Web
## Gerado via JavaScript

Este PDF foi criado a partir de uma **requisição web**.
`;

converterMarkdownPDF(markdown, 'documento_web.pdf');
```

## 🔧 Testando a API

Execute o script de teste para verificar todas as funcionalidades:

```bash
python testar_api.py
```

Ou teste manualmente cada endpoint.

## ⚡ Formatos Suportados

A API suporta os seguintes elementos Markdown:

| Elemento | Sintaxe | Exemplo |
|----------|---------|---------|
| Título 1 | `# Texto` | # Título Principal |
| Título 2 | `## Texto` | ## Subtítulo |
| Título 3 | `### Texto` | ### Subsubtítulo |
| Negrito | `**texto**` | **texto em negrito** |
| Itálico | `*texto*` | *texto em itálico* |
| Código inline | `` `código` `` | `print("hello")` |
| Bloco de código | ``` ```código``` ``` | Bloco destacado |
| Lista | `- item` | • Item da lista |
| Lista numerada | `1. item` | 1. Item numerado |
| Citação | `> texto` | Bloco de citação |

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

## 🔐 Considerações de Segurança

- A API não faz autenticação por padrão
- Arquivos temporários são automaticamente removidos
- Limite de tamanho do texto pode ser configurado no Flask
- Para produção, considere adicionar rate limiting

## 📊 Performance

- Conversões típicas: 50-500ms
- Tamanho máximo recomendado: 10MB de texto
- Arquivos temporários são limpos automaticamente
- Suporte a requisições concorrentes

## 🐛 Resolução de Problemas

### Servidor não inicia
```bash
# Verificar se a porta está livre
netstat -an | findstr 9000

# Verificar dependências
pip list | findstr -i "flask reportlab markdown"
```

### Erro de conversão
- Verificar se o texto Markdown está válido
- Verificar logs do servidor
- Testar com texto simples primeiro

### Problemas de encoding
- Garantir que o texto está em UTF-8
- Verificar caracteres especiais no Markdown

---

**Pronto para usar! 🎉**