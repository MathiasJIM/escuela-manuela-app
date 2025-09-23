from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr

class MateriaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre de la materia")


class MateriaCreate(MateriaBase):
    pass


class MateriaUpdate(MateriaBase):
    pass


class ProfesorBase(BaseModel):
    id_profesor: UUID
    nombre: str
    correo: EmailStr

    class Config:
        orm_mode = True


class Materia(MateriaBase):
    id_materia: UUID

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id_materia": "550e8400-e29b-41d4-a716-446655440000",
                "nombre": "Matemáticas"
            }
        }


class MateriaConProfesores(Materia):
    profesores: List[ProfesorBase] = []

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id_materia": "550e8400-e29b-41d4-a716-446655440000",
                "nombre": "Matemáticas",
                "profesores": [
                    {
                        "id_profesor": "550e8400-e29b-41d4-a716-446655440001",
                        "nombre": "Juan Pérez",
                        "correo": "juan.perez@escuela.edu"
                    }
                ]
            }
        }
