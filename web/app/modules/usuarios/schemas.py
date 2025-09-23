from pydantic import BaseModel, EmailStr, UUID4, validator
from typing import Optional, Literal

class UsuarioBase(BaseModel):
    correo: EmailStr
    nombre: str
    rol: Literal["direccion", "profesor", "padre"]
    activo: bool
    foto: Optional[str] = None


class UsuarioOut(UsuarioBase):
    id_usuario: UUID4

    class Config:
        orm_mode = True


class UsuarioLogin(BaseModel):
    correo: EmailStr
    contrasena: str


class UsuarioCreate(BaseModel):
    correo: EmailStr
    nombre: str
    rol: Literal["direccion", "profesor", "padre"]
    contrasena: Optional[str] = None
    activo: bool = True
    foto: Optional[str] = None


class RegistroResponse(BaseModel):
    usuario: UsuarioOut
    contrasena_generada: Optional[str] = None


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


class CambioContrasenaResponse(BaseModel):
    mensaje: str