from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Text, DECIMAL, JSON, SmallInteger, BigInteger, TinyInteger, VARCHAR, CHAR, DATE, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Rol(Base):
    __tablename__ = 'roles'
    rol_id = Column(SmallInteger(unsigned=True), primary_key=True, autoincrement=True)
    rol_codigo = Column(String(32), nullable=False, unique=True)
    rol_nombre = Column(String(80), nullable=False)
    creado_en = Column(DateTime, nullable=False, default='CURRENT_TIMESTAMP')
    actualizado_en = Column(DateTime, nullable=False, default='CURRENT_TIMESTAMP', onupdate='CURRENT_TIMESTAMP')

class Usuario(Base):
    __tablename__ = 'usuarios'
    usr_id = Column(BigInteger(unsigned=True), primary_key=True, autoincrement=True)
    usr_dni = Column(String(12), nullable=True)
    usr_correo = Column(String(190), nullable=False, unique=True)
    usr_contrasena = Column(CHAR(60), nullable=False)
    usr_nombre = Column(String(150), nullable=False)
    usr_apellido = Column(String(150), nullable=False)
    usr_usuario = Column(String(150), nullable=False)
    rol_id = Column(SmallInteger(unsigned=True), ForeignKey('roles.rol_id'), nullable=False)
    usr_activo = Column(TinyInteger(1), nullable=False, default=1)
    creado_en = Column(DateTime, nullable=False, default='CURRENT_TIMESTAMP')
    actualizado_en = Column(DateTime, nullable=False, default='CURRENT_TIMESTAMP', onupdate='CURRENT_TIMESTAMP')
    eliminado_en = Column(DateTime, nullable=True)

    rol = relationship('Rol')
