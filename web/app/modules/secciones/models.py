from uuid import UUID
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import uuid


class Seccion(Base):
    __tablename__ = "seccion"

    id_seccion = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(20), nullable=False)
    grado = Column(String(20), nullable=False)
    id_profesor_guia = Column(PostgresUUID(as_uuid=True), ForeignKey("usuario.id_usuario"), nullable=True)
    id_anio = Column(PostgresUUID(as_uuid=True), ForeignKey("anio_lectivo.id_anio", ondelete="CASCADE"), nullable=False)
