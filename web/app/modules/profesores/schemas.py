from pydantic import BaseModel, UUID4, EmailStr
from typing import List, Optional

class ProfesorBase(BaseModel):
    id_profesor: UUID4
    nombre: str
    correo: str
    
    class Config:
        orm_mode = True
        from_attributes = True

class ProfesorCreate(BaseModel):
    nombre: str
    correo: EmailStr

class ProfesorUpdate(BaseModel):
    nombre: str
    correo: EmailStr

class ProfesorCreated(BaseModel):
    id_profesor: UUID4
    nombre: str
    correo: str
    
    class Config:
        orm_mode = True
        from_attributes = True

class ProfesorMateriasAsignacion(BaseModel):
    id_profesor: UUID4
    id_materias: List[UUID4]
    id_anio: UUID4

class ProfesorSeccionesAsignacion(BaseModel):
    id_profesor: UUID4
    id_secciones: List[UUID4]

class ProfesorConMaterias(ProfesorBase):
    materias: List[dict]

class ProfesorConSecciones(ProfesorBase):
    secciones: List[dict]

class ProfesorCompleto(ProfesorBase):
    materias: List[dict]
    secciones: List[dict]
