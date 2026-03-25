from fastapi import FastAPI
from app.routes import transacao

#inicialização

app = FastAPI(title="PI Zambom")

app.include_router(transacao.router)

