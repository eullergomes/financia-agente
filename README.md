# 💸 FinanCIA — Agente Financeiro com LLaMA (Groq)

Um agente inteligente em pt-BR que entende frases como:

> **"gastei 80 reais em pizza ontem"**  
> **"em qual categoria eu mais gastei este mês?"**  
> **"quanto gastei em transporte em outubro?"**

Ele:

- 🧠 Usa **LLaMA rodando na Groq** para entender linguagem natural
- 🔧 Usa **function calling (tools)** para registrar e consultar despesas
- 📁 Salva tudo em um **arquivo JSON** simples
- 💬 Responde em linguagem natural, de forma amigável e objetiva

Projeto pensado para demonstrar, em pouco código, conceitos de:

- **GenAI aplicada**
- **Agentes com ferramentas**
- **Integração IA + lógica de negócio + persistência**

---

## 🚀 Demonstração

### Registrar uma despesa

> Você: `gastei 80 reais em pizza ontem`  
> Agente:  
> `Registrei uma despesa de R$ 80,00 em pizza na categoria alimentação com a data de ontem. 🍕`

---

### Ver categoria com maior gasto no mês

> Você: `em qual categoria eu mais gastei este mês?`  
> Agente:  
> `Neste mês, a categoria em que você mais gastou foi alimentação, com um total de R$ 320,00.`

---

## 🧠 Arquitetura

Fluxo básico:

```text
Usuário → LLaMA (Groq) → decide qual ferramenta chamar → função Python grava/consulta JSON → LLaMA gera resposta explicando o resultado
```

---

## 🔐 Configuração da Chave (GROQ_API_KEY)

1. Crie um arquivo `.env` na raiz do projeto (mesmo diretório em que você roda `python -m src.cli`).
2. Adicione sua chave:

```
GROQ_API_KEY=sk_sua_chave_aqui
```

3. Instale dependências:

```powershell
pip install -r requirements.txt
```

4. Execute:

```powershell
python -m src.cli
```

O código usa `python-dotenv` para carregar automaticamente o `.env`. Se a variável não existir, lança erro claro antes de iniciar o agente.

---

## 🛠 Ferramentas Internas

O agent usa function calling para três operações principais:

- `tool_add_expense`: registra uma nova despesa.
- `tool_get_top_category`: retorna a categoria com maior gasto em período.
- `tool_get_summary`: resumo de gastos por categoria.

Formato interno das despesas (JSON em `data/expenses.json`):

```json
{
  "amount": 80.0,
  "category": "alimentacao",
  "description": "pizza",
  "date": "2025-11-18",
  "currency": "BRL"
}
```

---

## ▶️ Uso Rápido

Perguntas exemplos que acionam ferramentas automaticamente:

| Entrada                                     | Ação             |
| ------------------------------------------- | ---------------- |
| "gastei 42 reais em uber hoje"              | Registra despesa |
| "quanto gastei em transporte este mês"      | Resumo categoria |
| "qual categoria mais gastei no mês passado" | Top categoria    |

O modelo decide quando chamar a tool; a resposta final sempre é natural e curta.

---

## 🧪 Teste Manual da Variável

Se quiser validar rapidamente o carregamento da chave:

```powershell
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(bool(os.getenv('GROQ_API_KEY')))"
```

Resultado esperado: `True`.

---
