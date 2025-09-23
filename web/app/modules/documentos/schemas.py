from typing import Optional, List
from pydantic import BaseModel, UUID4, HttpUrl
from datetime import datetime
from enum import Enum


class DestinatarioEnum(str, Enum):
    DIRECCION = "direccion"
    PROFESORES = "profesores"
    PADRES = "padres"
    TODOS = "todos"


class TipoDocumentoEnum(str, Enum):
    PLANEAMIENTO = "planeamiento"
    CIRCULAR = "circular"
    MATERIAL = "material"
    INFORME = "informe"
    OTRO = "otro"


class DocumentoBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    tipo: TipoDocumentoEnum
    destinatario: DestinatarioEnum = DestinatarioEnum.TODOS


class DocumentoCreate(DocumentoBase):
    archivo: str  # Enlace al documento (Google Drive, OneDrive, etc.)


class DocumentoUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    tipo: Optional[TipoDocumentoEnum] = None
    archivo: Optional[str] = None
    destinatario: Optional[DestinatarioEnum] = None


class DocumentoOut(DocumentoBase):
    id_documento: UUID4
    archivo: str
    fecha_subida: datetime
    subido_por: Optional[UUID4] = None

    class Config:
        orm_mode = True


class DocumentoList(BaseModel):
    documentos: List[DocumentoOut]

    class Config:
        orm_mode = True
