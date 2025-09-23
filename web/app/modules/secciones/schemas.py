from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr

class SeccionBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=20, description="Nombre de la sección")
    grado: str = Field(..., min_length=1, max_length=20, description="Grado de la sección")
    id_profesor_guia: Optional[UUID] = Field(None, description="ID del profesor guía")
    id_anio: UUID = Field(..., description="ID del año lectivo")


class SeccionCreate(SeccionBase):
    pass


class SeccionUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=20, description="Nombre de la sección")
    grado: Optional[str] = Field(None, min_length=1, max_length=20, description="Grado de la sección")
    id_profesor_guia: Optional[UUID] = Field(None, description="ID del profesor guía")
    id_anio: Optional[UUID] = Field(None, description="ID del año lectivo")


class ProfesorBase(BaseModel):
    id_profesor: UUID
    nombre: str
    correo: EmailStr

    class Config:
        orm_mode = True


class Seccion(SeccionBase):
    id_seccion: UUID
    profesor_guia_nombre: Optional[str] = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id_seccion": "550e8400-e29b-41d4-a716-446655440000",
                "nombre": "A",
                "grado": "Primer grado",
                "id_profesor_guia": "550e8400-e29b-41d4-a716-446655440001",
                "id_anio": "550e8400-e29b-41d4-a716-446655440002",
                "profesor_guia_nombre": "Juan Pérez"
            }
        }


class SeccionConProfesores(Seccion):
    profesores: List[ProfesorBase] = []

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id_seccion": "550e8400-e29b-41d4-a716-446655440000",
                "nombre": "A",
                "grado": "Primer grado",
                "id_profesor_guia": "550e8400-e29b-41d4-a716-446655440001",
                "id_anio": "550e8400-e29b-41d4-a716-446655440002",
                "profesores": [
                    {
                        "id_profesor": "550e8400-e29b-41d4-a716-446655440001",
                        "nombre": "Juan Pérez",
                        "correo": "juan.perez@escuela.edu"
                    }
                ]
            }
        }
