from sqlalchemy import Column, String, Text, Boolean, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base
import uuid


class Notificacion(Base):
    __tablename__ = "notificacion"

    id_notificacion = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_usuario = Column(UUID(as_uuid=True), ForeignKey("usuario.id_usuario", ondelete="CASCADE"))
    titulo = Column(String(100), nullable=False)
    mensaje = Column(Text, nullable=False)
    fecha = Column(DateTime, nullable=False, default=func.now())
    tipo = Column(String(20), nullable=False)
    leida = Column(Boolean, nullable=False, default=False)
    accionable = Column(Boolean, default=False)
    accion = Column(String(50), nullable=True)
    accion_texto = Column(String(50), nullable=True)
    accion_icono = Column(String(30), nullable=True)
    referencia_id = Column(UUID(as_uuid=True), nullable=True)
    referencia_tipo = Column(String(30), nullable=True)

    # Relación con el usuario
    usuario = relationship("Usuario", back_populates="notificaciones")
