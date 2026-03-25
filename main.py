from fastapi import FastAPI
from app.routes import transacao

app = FastAPI(title="PI Zambom")

app.include_router(transacao.router)
