from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Cliente(BaseModel):
    id_cliente: int
    nombre: str
    ciudad_origen_cuenta: str
    tipo: str

    class Config:
        from_attributes = True
        
class Cuenta(BaseModel):
    id_cuenta: int
    tipo_cuenta: str
    saldo: float
    id_cliente: int

    class Config:
        from_attributes = True
        
class Transaccion(BaseModel):
    id_transaccion: int
    tipo_transaccion: str
    monto: float
    fecha: datetime
    ciudad_origen: str
    id_cuenta: int

    class Config:
        from_attributes = True

class Reporte(BaseModel):
    id: int
    tipo: str
    parametros: str

    class Config:
        from_attributes = True
