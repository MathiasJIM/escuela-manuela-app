from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from enum import Enum


class TipoNotificacion(str, Enum):
    sistema = "sistema"
    cita = "cita"
    material = "material"
    calendario = "calendario"
    mensaje = "mensaje"
    alerta = "alerta"
    aviso = "aviso"


class NotificacionBase(BaseModel):
    titulo: str
    mensaje: str
    tipo: TipoNotificacion
    accionable: Optional[bool] = False
    accion: Optional[str] = None
    accion_texto: Optional[str] = None
    accion_icono: Optional[str] = None
    referencia_id: Optional[UUID] = None
    referencia_tipo: Optional[str] = None


class NotificacionCreate(NotificacionBase):
    id_usuario: UUID


class NotificacionUpdate(BaseModel):
    leida: Optional[bool] = None
    accionable: Optional[bool] = None
    accion: Optional[str] = None
    accion_texto: Optional[str] = None
    accion_icono: Optional[str] = None


class NotificacionOut(NotificacionBase):
    id_notificacion: UUID
    id_usuario: UUID
    fecha: datetime
    leida: bool

    class Config:
        orm_mode = True


class NotificacionesResponse(BaseModel):
    notificaciones: List[NotificacionOut]
    total: int
    no_leidas: int
