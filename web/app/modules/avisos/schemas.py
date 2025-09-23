from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class AvisoBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=100, description="Título del aviso")
    contenido: str = Field(..., description="Contenido del aviso")
    fecha_envio: datetime = Field(..., description="Fecha y hora del aviso")
    destinatario: str = Field(..., description="Destinatario del aviso (todos, profesores o padres)")


class AvisoCreate(AvisoBase):
    pass


class AvisoUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=100, description="Título del aviso")
    contenido: Optional[str] = Field(None, description="Contenido del aviso")
    fecha_envio: Optional[datetime] = Field(None, description="Fecha y hora del aviso")
    destinatario: Optional[str] = Field(None, description="Destinatario del aviso (todos, profesores o padres)")


class Aviso(AvisoBase):
    id_aviso: UUID

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id_aviso": "550e8400-e29b-41d4-a716-446655440000",
                "titulo": "Reunión de padres",
                "contenido": "Reunión general de padres de familia",
                "fecha_envio": "2025-06-01T14:00:00",
                "destinatario": "todos"
            }
        }
