import os
import httpx
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from bson import ObjectId
from dotenv import load_dotenv

from app.database import transacoes_collection
from app.models import TransacaoCreate, TransacaoResponse

load_dotenv()

USERS_API_URL = os.getenv("USERS_API_URL", "http://18.228.48.67")

router = APIRouter(prefix="/transacao", tags=["Transações"])

def serialize(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


@router.get("", response_model=list[TransacaoResponse])
async def listar_transacoes(id_cliente: Optional[str] = Query(default=None)):
    filtro = {}
    if id_cliente:
        filtro["id_cliente"] = id_cliente

    cursor = transacoes_collection.find(filtro)
    transacoes = []
    async for doc in cursor:
        transacoes.append(serialize(doc))
    return transacoes


@router.delete("/{id}", status_code=200)
async def deletar_transacao(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    resultado = await transacoes_collection.delete_one({"_id": ObjectId(id)})
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Transação não encontrada")


@router.post("", response_model=TransacaoResponse, status_code=200)
async def criar_transacao(transacao: TransacaoCreate):
    async with httpx.AsyncClient() as client:
        try:
            resposta = await client.get(f"{USERS_API_URL}/users/{transacao.id_cliente}")
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Serviço de usuários indisponível")

    if resposta.status_code == 404:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    if resposta.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro ao consultar serviço de usuários")

    usuario = resposta.json()
    email_cliente = usuario.get("email", "")

    valor_total = transacao.quantidade * transacao.preco_unitario

    doc = {
        "id_cliente": transacao.id_cliente,
        "email_cliente": email_cliente,
        "codigo_acao": transacao.codigo_acao,
        "quantidade": transacao.quantidade,
        "preco_unitario": transacao.preco_unitario,
        "valor_total": valor_total,
        "data_transacao": transacao.data_transacao.isoformat(),
    }

    resultado = await transacoes_collection.insert_one(doc)
    doc["id"] = str(resultado.inserted_id)
    doc.pop("_id")
    return doc
