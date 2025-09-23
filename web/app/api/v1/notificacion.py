from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel

from app.api.v1.deps import get_db, get_current_user
from app.modules.notificacion import crud
from app.modules.notificacion.schemas import (
    NotificacionCreate,
    NotificacionOut,
    NotificacionUpdate,
    NotificacionesResponse
)
from app.modules.usuarios.schemas import UsuarioOut

router = APIRouter()


@router.get("/obtener-notificaciones", response_model=NotificacionesResponse)
async def obtener_notificaciones(
    skip: int = Query(0, description="Número de registros a omitir para paginación"),
    limit: int = Query(100, description="Número máximo de registros a devolver"),
    solo_no_leidas: bool = Query(False, description="Si es True, solo devuelve notificaciones no leídas"),
    db: Session = Depends(get_db),
    usuario_actual: UsuarioOut = Depends(get_current_user)
):
    """
    Obtiene las notificaciones del usuario actual.
    
    - **skip**: Número de registros a omitir (paginación)
    - **limit**: Número máximo de registros a devolver
    - **solo_no_leidas**: Si es True, solo devuelve notificaciones no leídas
    
    Retorna un objeto con:
    - **notificaciones**: Lista de notificaciones
    - **total**: Número total de notificaciones (con filtros aplicados)
    - **no_leidas**: Número de notificaciones no leídas (sin filtros)
    """
    try:
        resultado = await crud.obtener_notificaciones_usuario(
            db=db,
            id_usuario=usuario_actual.id_usuario,
            skip=skip,
            limit=limit,
            solo_no_leidas=solo_no_leidas
        )
        
        return NotificacionesResponse(
            notificaciones=resultado["notificaciones"],
            total=resultado["total"],
            no_leidas=resultado["no_leidas"]
        )
    except Exception as e:
        # Registrar el error para depuración
        print(f"Error al obtener notificaciones: {str(e)}")
        # Devolver una respuesta vacía en lugar de un error 500
        return NotificacionesResponse(
            notificaciones=[],
            total=0,
            no_leidas=0
        )


@router.post("/crear-notificacion", response_model=NotificacionOut)
async def crear_notificacion(
    notificacion: NotificacionCreate,
    db: Session = Depends(get_db),
    usuario_actual: UsuarioOut = Depends(get_current_user)
):
    """
    Crea una nueva notificación.
    
    Solo usuarios con rol "direccion" pueden crear notificaciones para otros usuarios.
    Los usuarios con otros roles solo pueden crear notificaciones para sí mismos.
    
    - **notificacion**: Datos de la notificación a crear
    """
    # Verificar permisos
    if usuario_actual.rol != "direccion" and notificacion.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(
            status_code=403,
            detail="No tiene permisos para crear notificaciones para otros usuarios"
        )
    
    return await crud.crear_notificacion(db=db, notificacion=notificacion)


class NotificacionMasivaCreate(BaseModel):
    ids_usuarios: List[UUID]
    titulo: str
    mensaje: str
    tipo: str = "sistema"
    accionable: bool = False
    accion: Optional[str] = None
    accion_texto: Optional[str] = None
    accion_icono: Optional[str] = None
    referencia_id: Optional[UUID] = None
    referencia_tipo: Optional[str] = None


@router.post("/crear-notificacion-masiva", response_model=dict)
async def crear_notificacion_masiva(
    datos: NotificacionMasivaCreate,
    db: Session = Depends(get_db),
    usuario_actual: UsuarioOut = Depends(get_current_user)
):
    """
    Crea la misma notificación para múltiples usuarios.
    
    Solo usuarios con rol "direccion" pueden usar este endpoint.
    
    - **ids_usuarios**: Lista de IDs de usuarios destinatarios
    - **titulo**: Título de la notificación
    - **mensaje**: Mensaje de la notificación
    - **tipo**: Tipo de notificación (sistema, aviso, etc.)
    - **accionable**: Si la notificación permite acciones
    - **accion**: Tipo de acción
    - **accion_texto**: Texto del botón de acción
    - **accion_icono**: Icono del botón de acción
    - **referencia_id**: ID de referencia (ej: ID de aviso)
    - **referencia_tipo**: Tipo de referencia (ej: "aviso")
    """
    # Verificar permisos (solo dirección puede crear notificaciones masivas)
    if usuario_actual.rol != "direccion":
        raise HTTPException(
            status_code=403,
            detail="Solo usuarios con rol 'direccion' pueden crear notificaciones masivas"
        )
    
    # Verificar que la lista de usuarios no esté vacía
    if not datos.ids_usuarios:
        raise HTTPException(
            status_code=400,
            detail="La lista de usuarios destinatarios no puede estar vacía"
        )
    
    # Crear notificaciones masivas
    cantidad = await crud.crear_notificacion_masiva(
        db=db,
        ids_usuarios=datos.ids_usuarios,
        titulo=datos.titulo,
        mensaje=datos.mensaje,
        tipo=datos.tipo,
        accionable=datos.accionable,
        accion=datos.accion,
        accion_texto=datos.accion_texto,
        accion_icono=datos.accion_icono,
        referencia_id=datos.referencia_id,
        referencia_tipo=datos.referencia_tipo
    )
    
    return {
        "mensaje": f"Se han creado {cantidad} notificaciones correctamente",
        "cantidad": cantidad
    }


@router.get("/obtener-notificacion-id/{id_notificacion}", response_model=NotificacionOut)
async def obtener_notificacion(
    id_notificacion: UUID = Path(..., description="ID de la notificación"),
    db: Session = Depends(get_db),
    usuario_actual: UsuarioOut = Depends(get_current_user)
):
    """
    Obtiene una notificación específica por su ID.
    
    - **id_notificacion**: ID de la notificación a obtener
    """
    notificacion = await crud.obtener_notificacion(db=db, id_notificacion=id_notificacion)
    
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    
    # Verificar que la notificación pertenezca al usuario actual
    if notificacion.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(
            status_code=403,
            detail="No tiene permisos para acceder a esta notificación"
        )
    
    return notificacion


@router.patch("/actualizar-notificacion/{id_notificacion}", response_model=NotificacionOut)
async def actualizar_notificacion(
    datos_actualizacion: NotificacionUpdate,
    id_notificacion: UUID = Path(..., description="ID de la notificación"),
    db: Session = Depends(get_db),
    usuario_actual: UsuarioOut = Depends(get_current_user)
):
    """
    Actualiza una notificación existente.
    
    - **id_notificacion**: ID de la notificación a actualizar
    - **datos_actualizacion**: Datos a actualizar
    """
    notificacion = await crud.obtener_notificacion(db=db, id_notificacion=id_notificacion)
    
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    
    # Verificar que la notificación pertenezca al usuario actual
    if notificacion.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(
            status_code=403,
            detail="No tiene permisos para actualizar esta notificación"
        )
    
    return await crud.actualizar_notificacion(
        db=db,
        id_notificacion=id_notificacion,
        datos_actualizacion=datos_actualizacion
    )


@router.patch("/marcar-como-leida/{id_notificacion}", response_model=NotificacionOut)
async def marcar_como_leida(
    id_notificacion: UUID = Path(..., description="ID de la notificación"),
    db: Session = Depends(get_db),
    usuario_actual: UsuarioOut = Depends(get_current_user)
):
    """
    Marca una notificación como leída.
    
    - **id_notificacion**: ID de la notificación a marcar como leída
    """
    notificacion = await crud.obtener_notificacion(db=db, id_notificacion=id_notificacion)
    
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    
    # Verificar que la notificación pertenezca al usuario actual
    if notificacion.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(
            status_code=403,
            detail="No tiene permisos para actualizar esta notificación"
        )
    
    return await crud.marcar_como_leida(db=db, id_notificacion=id_notificacion)


@router.patch("/marcar-todas-como-leidas", response_model=dict)
async def marcar_todas_como_leidas(
    db: Session = Depends(get_db),
    usuario_actual: UsuarioOut = Depends(get_current_user)
):
    """
    Marca todas las notificaciones del usuario actual como leídas.
    
    Retorna el número de notificaciones actualizadas.
    """
    cantidad = await crud.marcar_todas_como_leidas(
        db=db,
        id_usuario=usuario_actual.id_usuario
    )
    
    return {"actualizadas": cantidad, "mensaje": "Notificaciones marcadas como leídas"}


@router.delete("/eliminar-notificacion/{id_notificacion}", response_model=dict)
async def eliminar_notificacion(
    id_notificacion: UUID = Path(..., description="ID de la notificación"),
    db: Session = Depends(get_db),
    usuario_actual: UsuarioOut = Depends(get_current_user)
):
    """
    Elimina una notificación específica.
    
    - **id_notificacion**: ID de la notificación a eliminar
    """
    notificacion = await crud.obtener_notificacion(db=db, id_notificacion=id_notificacion)
    
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    
    # Verificar que la notificación pertenezca al usuario actual
    if notificacion.id_usuario != usuario_actual.id_usuario:
        raise HTTPException(
            status_code=403,
            detail="No tiene permisos para eliminar esta notificación"
        )
    
    resultado = await crud.eliminar_notificacion(db=db, id_notificacion=id_notificacion)
    
    if resultado:
        return {"mensaje": "Notificación eliminada correctamente"}
    else:
        raise HTTPException(status_code=500, detail="Error al eliminar la notificación")
