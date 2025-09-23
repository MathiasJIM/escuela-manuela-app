from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class ProfesorMateria(Base):
    __tablename__ = "profesor_materia"

    id_profesor = Column(PostgresUUID(as_uuid=True), ForeignKey("profesor.id_profesor", ondelete="CASCADE"), primary_key=True)
    id_materia = Column(PostgresUUID(as_uuid=True), ForeignKey("materia.id_materia", ondelete="CASCADE"), primary_key=True)
    id_anio = Column(PostgresUUID(as_uuid=True), ForeignKey("anio_lectivo.id_anio"), primary_key=True)
