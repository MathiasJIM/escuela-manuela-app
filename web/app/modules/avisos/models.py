from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Text, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

from app.db.base_class import Base


class Aviso(Base):
    __tablename__ = "aviso"

    id_aviso = Column(PostgresUUID, primary_key=True, index=True, default=uuid4)
    titulo = Column(String(100), nullable=False)
    contenido = Column(Text, nullable=False)
    fecha_envio = Column(DateTime, nullable=False, default=lambda: datetime.now())
    destinatario = Column(String(20), nullable=False)
