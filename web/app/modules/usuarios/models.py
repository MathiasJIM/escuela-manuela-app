from sqlalchemy import Column, String, Boolean, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.base_class import Base
from enum import Enum as PyEnum

class Rol(str, PyEnum):
    DIRECCION = "direccion"
    PROFESOR = "profesor"
    PADRE = "padre"

class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    rol = Column(SQLEnum("direccion", "profesor", "padre", name="rol_enum"), nullable=False)
    contrasena_hash = Column(Text, nullable=False)
    activo = Column(Boolean, default=False)
    foto = Column(Text, nullable=True)
    
    profesor = relationship("Profesor", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    notificaciones = relationship("Notificacion", back_populates="usuario", cascade="all, delete-orphan")

class Profesor(Base):
    __tablename__ = "profesor"
    
    id_profesor = Column(UUID(as_uuid=True), ForeignKey("usuario.id_usuario", ondelete="CASCADE"), primary_key=True)

    usuario = relationship("Usuario", back_populates="profesor")
