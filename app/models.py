from pydantic import BaseModel
from datetime import date


class TransacaoCreate(BaseModel):
    id_cliente: str
    codigo_acao: str
    quantidade: int
    preco_unitario: float
    data_transacao: date


class TransacaoResponse(BaseModel):
    id: str
    id_cliente: str
    email_cliente: str
    codigo_acao: str
    quantidade: int
    preco_unitario: float
    valor_total: float
    data_transacao: str
