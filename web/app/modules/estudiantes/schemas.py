from typing import Optional
from uuid import UUID
from datetime import date
from pydantic import BaseModel, Field


class EstudianteBase(BaseModel):
    cedula: str = Field(..., min_length=1, max_length=20, description="Cédula del estudiante")
    nombre: str = Field(..., min_length=1, max_length=50, description="Nombre del estudiante")
    primer_apellido: str = Field(..., min_length=1, max_length=50, description="Primer apellido del estudiante")
    segundo_apellido: str = Field(..., min_length=1, max_length=50, description="Segundo apellido del estudiante")


class EstudianteCreate(EstudianteBase):
    id_padre: Optional[UUID] = Field(None, description="ID del usuario padre")
    id_seccion: Optional[UUID] = Field(None, description="ID de la sección")
    id_anio: Optional[UUID] = Field(None, description="ID del año lectivo")


class EstudianteUpdate(BaseModel):
    cedula: Optional[str] = Field(None, min_length=1, max_length=20, description="Cédula del estudiante")
    nombre: Optional[str] = Field(None, min_length=1, max_length=50, description="Nombre del estudiante")
    primer_apellido: Optional[str] = Field(None, min_length=1, max_length=50, description="Primer apellido del estudiante")
    segundo_apellido: Optional[str] = Field(None, min_length=1, max_length=50, description="Segundo apellido del estudiante")
    id_padre: Optional[UUID] = Field(None, description="ID del usuario padre")
    id_seccion: Optional[UUID] = Field(None, description="ID de la sección")


class SeccionInfo(BaseModel):
    id_seccion: UUID
    nombre: str
    grado: str

    class Config:
        orm_mode = True

class Estudiante(EstudianteBase):
    id_estudiante: UUID
    id_padre: Optional[UUID] = None
    id_seccion: Optional[UUID] = None
    seccion: Optional[SeccionInfo] = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id_estudiante": "550e8400-e29b-41d4-a716-446655440000",
                "cedula": "1-1234-5678",
                "nombre": "Juan",
                "primer_apellido": "Pérez",
                "segundo_apellido": "Gómez",
                "id_padre": "550e8400-e29b-41d4-a716-446655440001",
                "seccion": {
                    "id_seccion": "550e8400-e29b-41d4-a716-446655440002",
                    "nombre": "1-A",
                    "grado": "Primero"
                }
            }
        }


class EstudianteWithCredentials(Estudiante):
    correo_padre: str
    contrasena_padre: str
    matriculado: Optional[bool] = None
    id_seccion: Optional[UUID] = None
    id_anio: Optional[UUID] = None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id_estudiante": "550e8400-e29b-41d4-a716-446655440000",
                "cedula": "1-1234-5678",
                "nombre": "Juan",
                "primer_apellido": "Pérez",
                "segundo_apellido": "Gómez",
                "id_padre": "550e8400-e29b-41d4-a716-446655440001",
                "correo_padre": "jperez1234@escmanuela.ed.cr",
                "contrasena_padre": "Abc123!xy"
            }
        }


class Matricula(BaseModel):
    id_matricula: UUID
    id_estudiante: UUID
    id_seccion: UUID
    id_anio: UUID
    fecha_matricula: date

    class Config:
        orm_mode = True
