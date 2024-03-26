from sqlalchemy.orm import Session
from app.db.models import Cliente as ClienteDB, Cuenta as CuentaDB, Transaccion as TransaccionDB
from app.schemas import Cliente as ClienteCreate, Cuenta, Transaccion as TransaccionCreate
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel
from sqlalchemy import func
#CREAR CCLIENTES

def crear_cliente(cliente: ClienteCreate, db: Session):
    cliente_data = cliente.dict()
    try:
        nuevo_cliente = ClienteDB(
            id_cliente = cliente_data["id_cliente"],
            nombre = cliente_data["nombre"],
            ciudad_origen_cuenta = cliente_data["ciudad_origen_cuenta"],
            tipo = cliente_data["tipo"].upper()
        )
        db.add(nuevo_cliente)
        db.commit()
        db.refresh(nuevo_cliente)
        return nuevo_cliente
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


#CREAR CUENTA


def crear_cuenta(cuenta: Cuenta, db: Session):
    
    # Validar si el cliente existe
    cliente = db.query(ClienteDB).filter(ClienteDB.id_cliente == cuenta.id_cliente).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El cliente no existe")

    # Crear la nueva cuenta
    try:
        nueva_cuenta = CuentaDB(
            tipo_cuenta=cuenta.tipo_cuenta,
            saldo=0.0,
            id_cliente=cuenta.id_cliente,
        )
        db.add(nueva_cuenta)
        db.commit()
        db.refresh(nueva_cuenta)
        return nueva_cuenta
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))





# Funcion realizar consignacion
class TransactionError(BaseModel):
    message: str


def realizar_consignacion(db: Session, transaccion: TransaccionCreate):
    try:
        cuenta = db.query(CuentaDB).filter(CuentaDB.id_cuenta == transaccion.id_cuenta).first()
        if cuenta:
            cuenta.saldo += Decimal(transaccion.monto)
            nueva_transaccion = TransaccionDB(
                id_cuenta=transaccion.id_cuenta,
                monto=transaccion.monto,
                tipo_transaccion=transaccion.tipo_transaccion,
                ciudad_origen=transaccion.ciudad_origen,
                fecha=datetime.now(),
            )
            db.add(nueva_transaccion)
            db.commit()
            transaccion_pydantic = TransaccionCreate.from_orm(nueva_transaccion)
            return transaccion_pydantic
        else:
            return TransactionError(message="Cuenta no encontrada")
    except IntegrityError:
        db.rollback()
        return TransactionError(message="Error al realizar la consignacion")


# Función para retirar dinero
def retirar_dinero(db: Session, transaccion: TransaccionCreate):
    try:
        cuenta = db.query(CuentaDB).filter(CuentaDB.id_cuenta == transaccion.id_cuenta).first()
        if cuenta:
            if cuenta.saldo >= transaccion.monto:  # Verificar si hay suficiente saldo
                cuenta.saldo -= Decimal(transaccion.monto)
                nueva_transaccion = TransaccionDB(
                    id_cuenta=transaccion.id_cuenta,
                    monto=transaccion.monto,
                    tipo_transaccion=transaccion.tipo_transaccion,
                    ciudad_origen=transaccion.ciudad_origen,
                    fecha=datetime.now(),
                )
                db.add(nueva_transaccion)
                db.commit()
                # Actualizar el saldo en la tabla de cuentas
                db.refresh(cuenta)
                return transaccion
            else:
                return TransactionError(message="Saldo insuficiente para realizar la transacción")
        else:
            return TransactionError(message="Cuenta no encontrada")
    except IntegrityError:
        db.rollback()
        return TransactionError(message="Error al realizar la transacción")



def consultar_saldo(db: Session, id_cuenta: int):
    cuenta = db.query(CuentaDB).filter(CuentaDB.id_cuenta == id_cuenta).first()
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    return cuenta

def consultar_movimientos(db: Session, id_cuenta: int):
    movimientos = db.query(TransaccionDB).filter(TransaccionDB.id_cuenta == id_cuenta).order_by(TransaccionDB.fecha.desc()).all()
    if not movimientos:
        raise HTTPException(status_code=404, detail="No hay movimientos para esta cuenta")
    return movimientos

def generar_extracto_mensual(db: Session, id_cuenta: int, anio: int, mes: int):
    try:
        fecha_inicio = date(anio, mes, 1)
        fecha_fin = date(anio, mes + 1, 1) if mes < 12 else date(anio + 1, 1, 1)
        extracto = db.query(TransaccionDB).filter(
            TransaccionDB.id_cuenta == id_cuenta,
            TransaccionDB.fecha >= fecha_inicio,
            TransaccionDB.fecha < fecha_fin
        ).order_by(TransaccionDB.fecha).all()
        if not extracto:
            raise HTTPException(status_code=404, detail="No hay movimientos para este periodo")
        return extracto
    except ValueError:
        raise HTTPException(status_code=400, detail="Fecha inválida")
    
# Función para listar clientes con el número de transacciones para un mes particular
def listar_clientes_con_transacciones_por_mes(db: Session, anio: int, mes: int):
    try:
        clientes_con_transacciones = db.query(ClienteDB.id_cliente, ClienteDB.nombre, func.count(TransaccionDB.id_transaccion).label('num_transacciones')) \
            .join(TransaccionDB, ClienteDB.id_cliente == TransaccionDB.id_cliente) \
            .filter(func.extract('year', TransaccionDB.fecha) == anio) \
            .filter(func.extract('month', TransaccionDB.fecha) == mes) \
            .group_by(ClienteDB.id_cliente, ClienteDB.nombre) \
            .order_by(func.count(TransaccionDB.id_transaccion).desc()) \
            .all()
        return clientes_con_transacciones
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Función para obtener clientes que retiran dinero fuera de la ciudad de origen de la cuenta
def obtener_clientes_retiran_fuera_ciudad_origen(db: Session):
    try:
        clientes_retiran_fuera_ciudad = db.query(ClienteDB.id_cliente, ClienteDB.nombre, func.sum(TransaccionDB.monto).label('total_retirado')) \
            .join(TransaccionDB, ClienteDB.id_cliente == TransaccionDB.id_cliente) \
            .filter(TransaccionDB.tipo_transaccion == 'retiro') \
            .filter(ClienteDB.ciudad_origen_cuenta != TransaccionDB.ciudad_origen) \
            .group_by(ClienteDB.id_cliente, ClienteDB.nombre) \
            .having(func.sum(TransaccionDB.monto) > 1000000) \
            .all()
        return clientes_retiran_fuera_ciudad
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))