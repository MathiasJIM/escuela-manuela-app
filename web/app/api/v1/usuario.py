from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Tuple, List
import uuid
from app.modules.usuarios.schemas import UsuarioBase
from app.modules.usuarios.crud import eliminar_usuario_por_id, obtener_usuarios_por_rol
from app.api.v1.deps import get_db, get_current_user

router = APIRouter()


@router.get("/obtener-usuarios/{rol}", response_model=List[UsuarioBase])
def obtener_usuarios(db: Session = Depends(get_db), usuario_actual = Depends(get_current_user), rol: str = "profesor"):
    if usuario_actual.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permisos para obtener usuarios"
        )
    return obtener_usuarios_por_rol(db, rol)


@router.delete("/eliminar/{id_usuario}")
def eliminar_usuario(id_usuario: uuid.UUID, db: Session = Depends(get_db), usuario_actual = Depends(get_current_user)):
    if usuario_actual.rol != "direccion":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permisos para eliminar usuarios"
        )
    
    exito = eliminar_usuario_por_id(db, id_usuario)
    if not exito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuario no encontrado"
        )
    
    return {"mensaje": "Usuario eliminado correctamente"}


