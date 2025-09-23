from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_

from app.modules.notificacion.models import Notificacion
from app.modules.notificacion.schemas import NotificacionCreate, NotificacionUpdate


async def crear_notificacion(db: Session, notificacion: NotificacionCreate) -> Notificacion:

    db_notificacion = Notificacion(
        id_usuario=notificacion.id_usuario,
        titulo=notificacion.titulo,
        mensaje=notificacion.mensaje,
        tipo=notificacion.tipo,
        accionable=notificacion.accionable,
        accion=notificacion.accion,
        accion_texto=notificacion.accion_texto,
        accion_icono=notificacion.accion_icono,
        referencia_id=notificacion.referencia_id,
        referencia_tipo=notificacion.referencia_tipo
    )
    db.add(db_notificacion)
    db.commit()
    db.refresh(db_notificacion)
    return db_notificacion


async def obtener_notificaciones_usuario(
    db: Session, 
    id_usuario: UUID, 
    skip: int = 0, 
    limit: int = 100,
    solo_no_leidas: bool = False
) -> Dict[str, Any]:
    try:
        # Verificar que el ID de usuario sea válido
        if not id_usuario:
            return {
                "notificaciones": [],
                "total": 0,
                "no_leidas": 0
            }
            
        # Construir la consulta base
        query = db.query(Notificacion).filter(Notificacion.id_usuario == id_usuario)
        
        # Contar notificaciones no leídas
        try:
            no_leidas = db.query(func.count(Notificacion.id_notificacion)).filter(
                and_(
                    Notificacion.id_usuario == id_usuario,
                    Notificacion.leida == False
                )
            ).scalar() or 0
        except Exception as e:
            print(f"Error al contar notificaciones no leídas: {str(e)}")
            no_leidas = 0
        
        # Aplicar filtro de solo no leídas si es necesario
        if solo_no_leidas:
            query = query.filter(Notificacion.leida == False)
        
        # Contar total de notificaciones con filtros aplicados
        try:
            total = query.count()
        except Exception as e:
            print(f"Error al contar total de notificaciones: {str(e)}")
            total = 0
        
        # Obtener las notificaciones con paginación y ordenamiento
        try:
            notificaciones = query.order_by(desc(Notificacion.fecha)).offset(skip).limit(limit).all()
        except Exception as e:
            print(f"Error al obtener notificaciones: {str(e)}")
            notificaciones = []
        
        return {
            "notificaciones": notificaciones,
            "total": total,
            "no_leidas": no_leidas
        }
    except Exception as e:
        print(f"Error general en obtener_notificaciones_usuario: {str(e)}")
        # Devolver un resultado vacío en caso de error
        return {
            "notificaciones": [],
            "total": 0,
            "no_leidas": 0
        }


async def obtener_notificacion(db: Session, id_notificacion: UUID) -> Optional[Notificacion]:
    return db.query(Notificacion).filter(Notificacion.id_notificacion == id_notificacion).first()


async def actualizar_notificacion(
    db: Session, 
    id_notificacion: UUID, 
    datos_actualizacion: NotificacionUpdate
) -> Optional[Notificacion]:

    notificacion = await obtener_notificacion(db, id_notificacion)
    if not notificacion:
        return None
    
    datos_dict = datos_actualizacion.dict(exclude_unset=True)
    for key, value in datos_dict.items():
        setattr(notificacion, key, value)
    
    db.commit()
    db.refresh(notificacion)
    return notificacion


async def marcar_como_leida(db: Session, id_notificacion: UUID) -> Optional[Notificacion]:
    notificacion = await obtener_notificacion(db, id_notificacion)
    if not notificacion:
        return None
    
    notificacion.leida = True
    db.commit()
    db.refresh(notificacion)
    return notificacion


async def marcar_todas_como_leidas(db: Session, id_usuario: UUID) -> int:
    resultado = db.query(Notificacion).filter(
        and_(
            Notificacion.id_usuario == id_usuario,
            Notificacion.leida == False
        )
    ).update({"leida": True})
    
    db.commit()
    return resultado


async def eliminar_notificacion(db: Session, id_notificacion: UUID) -> bool:
    notificacion = await obtener_notificacion(db, id_notificacion)
    if not notificacion:
        return False
    
    db.delete(notificacion)
    db.commit()
    return True


async def crear_notificacion_sistema(
    db: Session,
    id_usuario: UUID,
    titulo: str,
    mensaje: str,
    accionable: bool = False,
    accion: Optional[str] = None,
    accion_texto: Optional[str] = None,
    accion_icono: Optional[str] = None,
    referencia_id: Optional[UUID] = None,
    referencia_tipo: Optional[str] = None
) -> Notificacion:

    notificacion = NotificacionCreate(
        id_usuario=id_usuario,
        titulo=titulo,
        mensaje=mensaje,
        tipo="sistema",
        accionable=accionable,
        accion=accion,
        accion_texto=accion_texto,
        accion_icono=accion_icono,
        referencia_id=referencia_id,
        referencia_tipo=referencia_tipo
    )
    
    return await crear_notificacion(db, notificacion)


async def crear_notificacion_masiva(
    db: Session,
    ids_usuarios: List[UUID],
    titulo: str,
    mensaje: str,
    tipo: str = "sistema",
    accionable: bool = False,
    accion: Optional[str] = None,
    accion_texto: Optional[str] = None,
    accion_icono: Optional[str] = None,
    referencia_id: Optional[UUID] = None,
    referencia_tipo: Optional[str] = None
) -> int:

    notificaciones = [
        Notificacion(
            id_usuario=id_usuario,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo,
            accionable=accionable,
            accion=accion,
            accion_texto=accion_texto,
            accion_icono=accion_icono,
            referencia_id=referencia_id,
            referencia_tipo=referencia_tipo
        )
        for id_usuario in ids_usuarios
    ]
    
    db.add_all(notificaciones)
    db.commit()
    
    return len(notificaciones)
