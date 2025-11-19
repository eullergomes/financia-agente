import os
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional, List

from dotenv import load_dotenv, find_dotenv
from groq import Groq

from . import tools

load_dotenv(dotenv_path=find_dotenv(), override=False)

_api_key = os.getenv("GROQ_API_KEY")
if not _api_key:
    raise RuntimeError(
        "GROQ_API_KEY não encontrada. Verifique se o arquivo .env está na raiz (mesmo diretório do comando) ou defina a variável no ambiente antes de executar."
    )

client = Groq(api_key=_api_key)

SYSTEM_PROMPT = """
Você é um agente financeiro pessoal em português do Brasil.

- Você recebe mensagens do usuário sobre gastos, orçamentos e dúvidas financeiras simples.
- Quando o usuário descreve um gasto, você DEVE chamar a ferramenta apropriada para registrar a despesa.
- Quando o usuário faz perguntas sobre quanto gastou, categorias, resumos, etc., você DEVE chamar as ferramentas de consulta.
- Seja sempre curto, claro e amigável.

Categorias padrão: alimentacao, transporte, lazer, moradia, saude, outros.
Se o usuário não informar categoria, escolha a mais provável e siga em frente.
Datas:
- "hoje" = data de hoje.
- "ontem", "mês passado" etc. podem ser interpretados aproximadamente.
Se não tiver certeza das datas, use a data de hoje.
"""

TOOLS_SCHEMA: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "tool_add_expense",
            "description": "Registra uma nova despesa do usuário.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "category": {
                        "type": "string",
                        "description": "Categoria da despesa (ex: alimentacao, transporte, lazer).",
                    },
                    "description": {
                        "type": "string",
                        "description": "Descrição curta da despesa (ex: pizza, uber, cinema).",
                    },
                    "date_str": {
                        "type": "string",
                        "description": "Data no formato YYYY-MM-DD (opcional).",
                    },
                    "currency": {
                        "type": "string",
                        "description": "Moeda, por padrão BRL.",
                        "default": "BRL",
                    },
                },
                "required": ["amount", "category", "description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_get_top_category",
            "description": "Retorna a categoria com maior gasto em um período.",
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {"type": "integer", "nullable": True},
                    "month": {"type": "integer", "nullable": True},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_get_summary",
            "description": "Resumo de gastos por categoria em um período.",
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {"type": "integer", "nullable": True},
                    "month": {"type": "integer", "nullable": True},
                },
                "required": [],
            },
        },
    },
]

FUNCTION_MAP = {
    "tool_add_expense": tools.tool_add_expense,
    "tool_get_top_category": tools.tool_get_top_category,
    "tool_get_summary": tools.tool_get_summary,
}


@dataclass
class AgentResponse:
    text: str
    tool_call: Optional[Dict[str, Any]] = None
    tool_result: Optional[Dict[str, Any]] = None


def call_llm(messages, tools=None, tool_choice="auto"):
    """
    Wrapper para a API de chat da Groq, usando modelo LLaMA.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        tools=tools,
        tool_choice=tool_choice,
        temperature=0.2,
    )
    return response


def run_agent(user_message: str) -> AgentResponse:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    # 1ª chamada: deixa o modelo decidir se precisa de tool
    resp = call_llm(messages, tools=TOOLS_SCHEMA, tool_choice="auto")
    msg = resp.choices[0].message

    # Se o modelo decidiu usar alguma ferramenta
    tool_calls = getattr(msg, "tool_calls", None)

    if tool_calls:
        tool_call = tool_calls[0]
        func_name = tool_call.function.name
        try:
            args = json.loads(tool_call.function.arguments or "{}")
        except json.JSONDecodeError:
            return AgentResponse(
                text="Tive um problema para entender os parâmetros da ferramenta.",
                tool_call={"name": func_name, "args": tool_call.function.arguments},
            )

        func = FUNCTION_MAP.get(func_name)
        if not func:
            return AgentResponse(
                text="Ocorreu um erro ao localizar a ferramenta interna.",
                tool_call={"name": func_name, "args": args},
            )

        result = func(**args)

        # 2ª chamada: devolve o resultado da ferramenta para o modelo explicar pro usuário
        messages.append(
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": func_name,
                            "arguments": json.dumps(args, ensure_ascii=False),
                        },
                    }
                ],
            }
        )
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": func_name,
                "content": json.dumps(result, ensure_ascii=False),
            }
        )

        followup = call_llm(messages)
        final_text = followup.choices[0].message.content

        return AgentResponse(
            text=final_text,
            tool_call={"name": func_name, "args": args},
            tool_result=result,
        )

    # Sem tool calling: resposta direta
    return AgentResponse(text=msg.content or "")
