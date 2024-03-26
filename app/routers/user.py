from fastapi import APIRouter, Depends,HTTPException
from app.schemas import Cliente,Cuenta
from app.db.database import get_db
from app.repository.user import crear_cliente, crear_cuenta, realizar_consignacion, retirar_dinero,consultar_saldo, consultar_movimientos, generar_extracto_mensual
from app.repository.user import listar_clientes_con_transacciones_por_mes, obtener_clientes_retiran_fuera_ciudad_origen
from sqlalchemy.orm import Session
from app.schemas import Cliente as ClienteCreate,Cuenta as CuentaCreate,Transaccion as TransaccionCreate,Reporte



router = APIRouter(
    prefix="/user",
    tags=["Users"]
)

@router.post("/cliente", response_model=Cliente)
async def crear_cliente_route(cliente: ClienteCreate, db: Session = Depends(get_db)):

    db_cliente = crear_cliente(cliente, db)
    return db_cliente


@router.post("/cuenta", response_model=Cuenta)
async def crear_cuenta_route(cuenta: CuentaCreate, db: Session = Depends(get_db)):

    db_cuenta = crear_cuenta(cuenta, db)
    return db_cuenta



@router.post("/consignacion", response_model=TransaccionCreate)
async def realizar_consignacion_route(transaccion: TransaccionCreate, db: Session = Depends(get_db)):
   
        db_transaccion = realizar_consignacion(db,transaccion) 
        return db_transaccion
    
    
@router.post("/retiro", response_model=TransaccionCreate)
async def realizar_consignacion_route(transaccion: TransaccionCreate, db: Session = Depends(get_db)):
   
        db_transaccion_retiro = retirar_dinero(db,transaccion) 
        return db_transaccion_retiro
    

@router.get("/saldo/{id_cuenta}", response_model=Cuenta)
async def saldo(id_cuenta: int, db: Session = Depends(get_db)):
    return consultar_saldo(db, id_cuenta)

@router.get("/movimientos/{id_cuenta}", response_model=list[TransaccionCreate])
async def movimientos(id_cuenta: int, db: Session = Depends(get_db)):
    return consultar_movimientos(db, id_cuenta)

@router.get("/extracto/{id_cuenta}/{anio}/{mes}", response_model=list[TransaccionCreate])
async def extracto(id_cuenta: int, anio: int, mes: int, db: Session = Depends(get_db)):
    return generar_extracto_mensual(db, id_cuenta, anio, mes)

@router.get("/clientes-transacciones/{anio}/{mes}", response_model=list[Cliente])
async def listar_clientes_con_transacciones_por_mes_route(anio: int, mes: int, db: Session = Depends(get_db)):
    return listar_clientes_con_transacciones_por_mes(db, anio, mes)

@router.get("/clientes-retiran-fuera-ciudad", response_model=list[Cliente])
async def obtener_clientes_retiran_fuera_ciudad_origen_route(db: Session = Depends(get_db)):
    return obtener_clientes_retiran_fuera_ciudad_origen(db)