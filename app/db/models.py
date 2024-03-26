from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Cliente(Base):
    __tablename__ = 'cliente'

    id_cliente = Column(Integer, primary_key=True, autoincrement=False)
    nombre = Column(String(255), nullable=False)
    ciudad_origen_cuenta = Column(String(255), nullable=False)
    tipo = Column(String(20), nullable=False)
    cuentas = relationship("Cuenta", back_populates="cliente")

class Cuenta(Base):
    __tablename__ = 'cuenta'

    id_cuenta = Column(Integer, primary_key=True)
    tipo_cuenta = Column(String(255), nullable=False)
    saldo = Column(Numeric(precision=10, scale=2), nullable=False)
    id_cliente = Column(Integer, ForeignKey('cliente.id_cliente'))

    cliente = relationship("Cliente", back_populates="cuentas")
    transacciones = relationship("Transaccion", back_populates="cuenta")

class Transaccion(Base):
    __tablename__ = 'transaccion'

    id_transaccion = Column(Integer, primary_key=True)
    fecha = Column(DateTime, nullable=False)
    tipo_transaccion = Column(String(255), nullable=False)
    monto = Column(Numeric(precision=10, scale=2), nullable=False)
    ciudad_origen = Column(String(255), nullable=False)  # Nueva columna para la ciudad de origen de la transacción
    id_cuenta = Column(Integer, ForeignKey('cuenta.id_cuenta'))

    cuenta = relationship("Cuenta", back_populates="transacciones")

