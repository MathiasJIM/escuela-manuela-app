from uuid import UUID
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from app.db.base_class import Base
import uuid


class Materia(Base):
    """Modelo para la tabla materias"""
    __tablename__ = "materia"

    id_materia = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), nullable=False)
