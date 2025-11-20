import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path

from src.agent import run_agent

app = FastAPI(
    title="FinanCIA API",
    description="API do agente financeiro com LLaMA + Groq",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    tool: str | None = None
    tool_args: dict | None = None
    tool_result: dict | None = None


@app.get("/")
async def root():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"error": "index.html não encontrado", "expected_path": str(index_file)}

@app.get("/styles.css")
async def styles():
    css_file = FRONTEND_DIR / "styles.css"
    if css_file.exists():
        return FileResponse(css_file, media_type="text/css")
    return FileResponse(content="/* styles.css ausente */", media_type="text/css")

@app.get("/script.js")
async def script():
    js_file = FRONTEND_DIR / "script.js"
    if js_file.exists():
        return FileResponse(js_file, media_type="application/javascript")
    return FileResponse(content="console.warn('script.js ausente');", media_type="application/javascript")


@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    agent_response = run_agent(payload.message)
    return ChatResponse(
        reply=agent_response.text,
        tool=agent_response.tool_call.get("name") if agent_response.tool_call else None,
        tool_args=agent_response.tool_call.get("args") if agent_response.tool_call else None,
        tool_result=agent_response.tool_result if agent_response.tool_result else None,
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
