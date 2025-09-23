from typing import Optional
from datetime import date
from uuid import UUID
from pydantic import BaseModel, Field


class AnioLectivoBase(BaseModel):
    nombre: str = Field(..., min_length=4, max_length=9, description="Nombre del año lectivo, por ejemplo: '2025'")
    fecha_inicio: date = Field(..., description="Fecha de inicio del año lectivo")
    fecha_fin: date = Field(..., description="Fecha de finalización del año lectivo")
    activo: bool = Field(False, description="Indica si el año lectivo está activo")


class AnioLectivoCreate(AnioLectivoBase):
    pass


class AnioLectivoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=4, max_length=9, description="Nombre del año lectivo")
    fecha_inicio: Optional[date] = Field(None, description="Fecha de inicio del año lectivo")
    fecha_fin: Optional[date] = Field(None, description="Fecha de finalización del año lectivo")
    activo: Optional[bool] = Field(None, description="Indica si el año lectivo está activo")


class AnioLectivo(AnioLectivoBase):
    id_anio: UUID = Field(..., description="ID único del año lectivo")

    class Config:
        orm_mode = True
