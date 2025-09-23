from sqlalchemy import Column, ForeignKey, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import uuid

# No necesitamos crear un modelo específico para padres ya que
# los padres son usuarios con rol "padre" en la tabla usuario
# y están relacionados con estudiantes a través de la tabla estudiante
