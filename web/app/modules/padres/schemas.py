from pydantic import BaseModel, UUID4, EmailStr, Field, validator
from typing import List, Optional, Dict

# Esquemas para información de estudiantes (hijos)
class EstudianteHijo(BaseModel):
    id_estudiante: UUID4
    nombre: str

    class Config:
        orm_mode = True

# Esquema para información de calificaciones
class NotaEstudiante(BaseModel):
    id_nota: UUID4
    id_estudiante: UUID4
    id_materia: UUID4
    nombre_materia: str
    tipo: str
    descripcion: Optional[str] = None
    calificacion: float
    fecha: str

    class Config:
        orm_mode = True

# Esquema para información de asistencia
class AsistenciaEstudiante(BaseModel):
    id_asistencia: UUID4
    id_estudiante: UUID4
    id_materia: UUID4
    nombre_materia: str
    fecha: str
    estado: str
    comentario: Optional[str] = None

    class Config:
        orm_mode = True

# Esquemas para administración de padres
class PadreBase(BaseModel):
    nombre: str
    correo: EmailStr
    activo: bool = True
    foto: Optional[str] = None

class PadreCreate(PadreBase):
    contrasena: Optional[str] = None

class PadreUpdate(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None
    activo: Optional[bool] = None
    foto: Optional[str] = None

class PadreOut(PadreBase):
    id_usuario: UUID4
    rol: str = "padre"
    
    class Config:
        orm_mode = True

class PadreOutWithHijos(PadreOut):
    hijos: List[EstudianteHijo] = []

class CambioContrasenaRequest(BaseModel):
    contrasena_actual: str
    nueva_contrasena: str
    
    @validator('nueva_contrasena')
    def validar_nueva_contrasena(cls, v, values):
        if 'contrasena_actual' in values and v == values['contrasena_actual']:
            raise ValueError('La nueva contraseña debe ser diferente a la actual')
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        return v

# Esquema para respuesta genérica
class MensajeResponse(BaseModel):
    mensaje: str
    
class ErrorResponse(BaseModel):
    detail: str
