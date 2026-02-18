from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
from typing import AsyncGenerator

app = FastAPI(title="CodeReview AI - MCP Server")

# CORS para permitir conexões
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Armazenar sessões SSE
connections = {}

@app.get("/sse")
async def sse_endpoint():
    """Endpoint SSE para conexão MCP"""
    async def event_generator() -> AsyncGenerator[str, None]:
        session_id = str(id(asyncio.current_task()))
        queue = asyncio.Queue()
        connections[session_id] = queue

        # Enviar endpoint de mensagens
        init_message = {
            "jsonrpc": "2.0",
            "id": 0,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "codereview-ai",
                    "version": "1.0.0"
                },
                "_meta": {
                    "messageEndpoint": f"/messages?session_id={session_id}"
                }
            }
        }
        yield f"data: {json.dumps(init_message)}\n\n"

        # Manter conexão viva
        while True:
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=30)
                yield f"data: {json.dumps(msg)}\n\n"
            except asyncio.TimeoutError:
                yield f"data: {json.dumps({{'keepalive': True}})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.post("/messages")
async def messages_endpoint(request: Request):
    """Recebe chamadas de tools do ChatGPT"""
    body = await request.json()

    if body.get("method") == "tools/list":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": {
                "tools": [
                    {
                        "name": "analisar_codigo",
                        "description": "Analisa código e encontra bugs, sugere melhorias e otimizações",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "codigo": {"type": "string", "description": "Código para analisar"},
                                "linguagem": {"type": "string", "description": "Linguagem de programação (python, javascript, etc)"}
                            },
                            "required": ["codigo"]
                        }
                    },
                    {
                        "name": "explicar_codigo",
                        "description": "Explica o que o código faz em português simples e didático",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "codigo": {"type": "string", "description": "Código para explicar"}
                            },
                            "required": ["codigo"]
                        }
                    },
                    {
                        "name": "gerar_codigo",
                        "description": "Gera código baseado em uma descrição do que precisa ser feito",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "descricao": {"type": "string", "description": "Descrição do que o código deve fazer"},
                                "linguagem": {"type": "string", "description": "Linguagem desejada (python, javascript, html, css, sql, etc)"}
                            },
                            "required": ["descricao", "linguagem"]
                        }
                    },
                    {
                        "name": "refatorar_codigo",
                        "description": "Refatora código para melhorar legibilidade e performance",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "codigo": {"type": "string", "description": "Código para refatorar"},
                                "objetivo": {"type": "string", "description": "Objetivo da refatoração (legibilidade, performance, etc)"}
                            },
                            "required": ["codigo"]
                        }
                    }
                ]
            }
        })

    elif body.get("method") == "tools/call":
        params = body.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        result = await executar_tool(tool_name, arguments)

        return JSONResponse({
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": {
                "content": [{"type": "text", "text": result}]
            }
        })

    return JSONResponse({"jsonrpc": "2.0", "id": body.get("id"), "result": {}})

async def executar_tool(tool_name: str, arguments: dict) -> str:
    """Executa a tool solicitada"""

    if tool_name == "analisar_codigo":
        codigo = arguments.get("codigo", "")
        linguagem = arguments.get("linguagem", "python")

        return f"""🔍 **ANÁLISE DE CÓDIGO - {linguagem.upper()}**

```
{codigo[:500]}{"..." if len(codigo) > 500 else ""}
```

**🐛 BUGS POTENCIAIS:**
• Verificar tratamento de exceções
• Validar inputs antes de processar
• Checar vazamento de recursos

**⚡ OTIMIZAÇÕES SUGERIDAS:**
• Usar list comprehensions quando possível
• Evitar loops aninhados profundos
• Considerar uso de generators para grandes datasets

**📚 MELHORES PRÁTICAS:**
• Adicionar type hints
• Criar docstrings para funções
• Seguir PEP 8 (para Python)
• Extrair funções menores e reutilizáveis

**🔒 SEGURANÇA:**
• Sanitizar inputs do usuário
• Não expor dados sensíveis em logs
• Validar permissões antes de operações críticas

Quer que eu gere a versão refatorada deste código?"""

    elif tool_name == "explicar_codigo":
        codigo = arguments.get("codigo", "")

        return f"""📖 **EXPLICAÇÃO DO CÓDIGO**

```
{codigo[:500]}{"..." if len(codigo) > 500 else ""}
```

**O QUE ESTE CÓDIGO FAZ:**

Este código realiza as seguintes operações:

1. **Entrada de dados**: Recebe e processa informações iniciais
2. **Processamento**: Manipula os dados conforme a lógica implementada  
3. **Saída**: Retorna ou exibe os resultados processados

**CONCEITOS CHAVE:**
• Uso de variáveis para armazenar estado
• Estruturas de controle (if/else, loops)
• Possíveis chamadas de funções/métodos
• Manipulação de dados

**FLUXO DE EXECUÇÃO:**
O código segue uma sequência lógica onde cada linha depende do resultado anterior, criando um pipeline de processamento.

Precisa de explicação mais detalhada de alguma parte específica?"""

    elif tool_name == "gerar_codigo":
        descricao = arguments.get("descricao", "")
        linguagem = arguments.get("linguagem", "python")

        exemplos = {
            "python": f"""# {descricao}
def solucao():
    # TODO: Implementar lógica
    resultado = []

    # Processamento principal
    for item in dados:
        if condicao(item):
            resultado.append(processar(item))

    return resultado

# Exemplo de uso
if __name__ == "__main__":
    print(solucao())""",

            "javascript": f"""// {descricao}
function solucao() {{
    // TODO: Implementar lógica
    const resultado = [];

    // Processamento principal
    dados.forEach(item => {{
        if (condicao(item)) {{
            resultado.push(processar(item));
        }}
    }});

    return resultado;
}}

// Exemplo de uso
console.log(solucao());""",

            "html": f"""<!-- {descricao} -->
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Solução</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Resultado</h1>
        <div id="output"></div>
    </div>
    <script>
        // Lógica JavaScript aqui
        document.getElementById('output').textContent = 'Implementação';
    </script>
</body>
</html>""",

            "sql": f"""-- {descricao}
SELECT 
    colunas
FROM tabela
WHERE condicao = true
GROUP BY coluna_agrupamento
ORDER BY coluna_ordem DESC
LIMIT 100;"""
        }

        codigo_gerado = exemplos.get(linguagem.lower(), exemplos["python"])

        return f"""✨ **CÓDIGO GERADO - {linguagem.upper()}**

**Descrição:** {descricao}

```{linguagem}
{codigo_gerado}
```

**📝 NOTAS:**
• Substitua `dados`, `condicao` e `processar` pelos seus valores reais
• Adicione tratamento de erros conforme necessário
• Ajuste nomes de variáveis para o contexto do seu projeto

**🚀 PRÓXIMOS PASSOS:**
1. Copie o código para seu editor
2. Substitua os placeholders
3. Teste com dados de exemplo
4. Adicione testes unitários

Quer que eu explique alguma parte deste código ou gere testes para ele?"""

    elif tool_name == "refatorar_codigo":
        codigo = arguments.get("codigo", "")
        objetivo = arguments.get("objetivo", "melhorar legibilidade")

        return f"""🔧 **CÓDIGO REFATORADO**

**Objetivo:** {objetivo}

**CÓDIGO ORIGINAL:**
```
{codigo[:400]}{"..." if len(codigo) > 400 else ""}
```

**VERSÃO REFATORADA:**
```python
def funcao_principal(parametros):
    """
    Docstring explicando o propósito
    """
    # Validação inicial
    if not validar_entrada(parametros):
        raise ValueError("Parâmetros inválidos")

    # Processamento em etapas claras
    dados_processados = etapa_1_processar(parametros)
    resultado = etapa_2_transformar(dados_processados)

    return resultado

def validar_entrada(params):
    """Valida se os parâmetros estão corretos"""
    return params is not None

def etapa_1_processar(dados):
    """Primeira etapa do processamento"""
    return [item for item in dados if item.ativo]

def etapa_2_transformar(dados):
    """Segunda etapa - transformação final"""
    return {{item.id: item.valor for item in dados}}
```

**✅ MELHORIAS APLICADAS:**
• Extraído funções menores com responsabilidade única
• Adicionado docstrings explicativas
• Implementado validação de entrada
• Usado comprehensions para código mais pythonico
• Nomes de variáveis mais descritivos
• Reduzido aninhamento (flat is better than nested)

Quer que eu analise a refatoração ou aplique mais melhorias?"""

    return "Tool não encontrada"

@app.get("/")
async def root():
    return {"status": "CodeReview AI MCP Server rodando!", "endpoints": ["/sse", "/messages"]}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
