import uuid
from datetime import date
from sqlalchemy import Column, String, ForeignKey, Date, UniqueConstraint, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from app.db.base_class import Base


class Estudiante(Base):
    __tablename__ = "estudiante"
    id_estudiante = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cedula = Column(String(20), nullable=False, unique=True)
    nombre = Column(String(50), nullable=False)
    primer_apellido = Column(String(50), nullable=False)
    segundo_apellido = Column(String(50), nullable=False)
    id_padre = Column(PostgresUUID(as_uuid=True), ForeignKey("usuario.id_usuario", ondelete="SET NULL"), nullable=True)
    id_seccion = Column(PostgresUUID(as_uuid=True), ForeignKey("seccion.id_seccion", ondelete="SET NULL"), nullable=True)


class Matricula(Base):
    __tablename__ = "matricula"
    id_matricula = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_estudiante = Column(PostgresUUID(as_uuid=True), ForeignKey("estudiante.id_estudiante", ondelete="CASCADE"), nullable=False)
    id_seccion = Column(PostgresUUID(as_uuid=True), ForeignKey("seccion.id_seccion", ondelete="CASCADE"), nullable=False)
    id_anio = Column(PostgresUUID(as_uuid=True), ForeignKey("anio_lectivo.id_anio"), nullable=False)
    fecha_matricula = Column(Date, default=date.today)
    
    __table_args__ = (UniqueConstraint('id_estudiante', 'id_anio', name='uq_estudiante_anio'),)


class Asistencia(Base):
    __tablename__ = "asistencia"
    id_asistencia = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_estudiante = Column(PostgresUUID(as_uuid=True), ForeignKey("estudiante.id_estudiante", ondelete="CASCADE"), nullable=False)
    id_materia = Column(PostgresUUID(as_uuid=True), ForeignKey("materia.id_materia"), nullable=False)
    id_anio = Column(PostgresUUID(as_uuid=True), ForeignKey("anio_lectivo.id_anio"), nullable=False)
    fecha = Column(Date, nullable=False)
    estado = Column(String(20), nullable=False)  # Presente, Ausente, Justificado, etc.
    comentario = Column(Text, nullable=True)


class Nota(Base):
    __tablename__ = "nota"
    id_nota = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_estudiante = Column(PostgresUUID(as_uuid=True), ForeignKey("estudiante.id_estudiante", ondelete="CASCADE"), nullable=False)
    id_materia = Column(PostgresUUID(as_uuid=True), ForeignKey("materia.id_materia"), nullable=False)
    id_anio = Column(PostgresUUID(as_uuid=True), ForeignKey("anio_lectivo.id_anio"), nullable=False)
    trimestre = Column(String(20), nullable=False)  # Primer trimestre, Segundo trimestre, etc.
    valor = Column(String(10), nullable=False)  # Calificación (puede ser numérica o alfabética)
    descripcion = Column(Text, nullable=True)  # Descripción o comentario sobre la nota
