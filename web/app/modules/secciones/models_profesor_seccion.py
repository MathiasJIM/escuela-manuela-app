from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class ProfesorSeccion(Base):
    __tablename__ = "profesor_seccion"

    id_profesor = Column(PostgresUUID(as_uuid=True), ForeignKey("profesor.id_profesor", ondelete="CASCADE"), primary_key=True)
    id_seccion = Column(PostgresUUID(as_uuid=True), ForeignKey("seccion.id_seccion", ondelete="CASCADE"), primary_key=True)
