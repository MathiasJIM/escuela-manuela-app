from uuid import UUID
from sqlalchemy import Column, String, Date, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import uuid


class AnioLectivo(Base):
    __tablename__ = "anio_lectivo"

    id_anio = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(9), unique=True, nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    activo = Column(Boolean, nullable=False, default=False)
