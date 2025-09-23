from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base_class import Base
import uuid


class Documento(Base):
    __tablename__ = "documento"

    id_documento = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    titulo = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    tipo = Column(String(30), nullable=False)  # Tipo de documento: planeamiento, circular, material, informe, otro
    archivo = Column(Text, nullable=False)  # Ahora almacena el enlace al documento (Google Drive, OneDrive, etc.)
    fecha_subida = Column(TIMESTAMP, server_default=func.now())
    subido_por = Column(UUID(as_uuid=True), ForeignKey("usuario.id_usuario", ondelete="SET NULL"), nullable=True)
    destinatario = Column(String(20), default="todos")
