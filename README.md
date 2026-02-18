# 🤖 CodeReview AI - MCP Server

Servidor MCP para análise e geração de código no ChatGPT.

## 🚀 Deploy no Render (Gratuito)

### Opção 1: Deploy Automático (Recomendado)
1. Crie um repositório no GitHub
2. Envie estes arquivos para o GitHub
3. Acesse [render.com](https://render.com)
4. Clique em "New +" → "Web Service"
5. Conecte seu GitHub e selecione o repositório
6. O Render detectará o `render.yaml` automaticamente
7. Clique em "Deploy"

### Opção 2: Deploy Manual
1. Acesse [render.com](https://render.com)
2. "New +" → "Web Service"
3. Upload dos arquivos ou conecte GitHub
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
5. Clique em "Deploy"

## 🔧 Configuração no ChatGPT

Quando o deploy terminar, você receberá uma URL tipo:
`https://codereview-ai-mcp.onrender.com`

No ChatGPT (Modo Desenvolvedor):
- **Nome:** CodeReview AI
- **URL do servidor MCP:** `https://SEU-APP.onrender.com/sse`
- **Autenticação:** Nenhuma

## 🛠️ Funcionalidades

| Tool | Descrição |
|------|-----------|
| `analisar_codigo` | Encontra bugs e sugere melhorias |
| `explicar_codigo` | Explica o código em português |
| `gerar_codigo` | Gera código a partir de descrição |
| `refatorar_codigo` | Melhora legibilidade e performance |

## 📁 Arquivos

- `main.py` - Servidor MCP completo
- `requirements.txt` - Dependências
- `render.yaml` - Configuração de deploy
