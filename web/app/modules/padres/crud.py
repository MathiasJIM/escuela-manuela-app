from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.modules.estudiantes.models import Asistencia
from app.modules.materias.models import Materia
from app.modules.estudiantes.models import Nota
from app.modules.estudiantes.models import Estudiante, Matricula
from app.modules.usuarios.models import Usuario
from app.modules.anio_lectivo.crud import get_anio_lectivo_activo
from app.core.security import hashear_password, verificar_password


def get_hijos_por_padre(db: Session, id_padre: UUID) -> List[Estudiante]:
    return db.query(Estudiante).filter(Estudiante.id_padre == id_padre).all()


def get_hijo_por_id(db: Session, id_estudiante: UUID, id_padre: UUID) -> Optional[Estudiante]:
    return db.query(Estudiante).filter(
        Estudiante.id_estudiante == id_estudiante,
        Estudiante.id_padre == id_padre
    ).first()


def get_notas_estudiante(db: Session, id_estudiante: UUID, id_anio: Optional[UUID] = None) -> List[Dict[str, Any]]:
    if not id_anio:
        anio_activo = get_anio_lectivo_activo(db)
        if anio_activo:
            id_anio = anio_activo.id_anio
    
    query = db.query(Nota, Materia.nombre.label("nombre_materia")).join(
        Materia, Nota.id_materia == Materia.id_materia
    ).filter(Nota.id_estudiante == id_estudiante)
    
    if id_anio:
        query = query.filter(Nota.id_anio == id_anio)
    
    results = query.all()
    
    notas_con_materia = []
    for nota, nombre_materia in results:
        nota_dict = {
            "id_nota": nota.id_nota,
            "id_estudiante": nota.id_estudiante,
            "id_materia": nota.id_materia,
            "nombre_materia": nombre_materia,
            "tipo": nota.tipo,
            "descripcion": nota.descripcion,
            "calificacion": nota.calificacion,
            "fecha": nota.fecha
        }
        notas_con_materia.append(nota_dict)
    
    return notas_con_materia


def get_asistencias_estudiante(db: Session, id_estudiante: UUID, id_anio: Optional[UUID] = None) -> List[Dict[str, Any]]:
    if not id_anio:
        anio_activo = get_anio_lectivo_activo(db)
        if anio_activo:
            id_anio = anio_activo.id_anio
    
    query = db.query(Asistencia, Materia.nombre.label("nombre_materia")).join(
        Materia, Asistencia.id_materia == Materia.id_materia
    ).filter(Asistencia.id_estudiante == id_estudiante)
    
    if id_anio:
        query = query.filter(Asistencia.id_anio == id_anio)
    
    results = query.all()
    
    asistencias_con_materia = []
    for asistencia, nombre_materia in results:
        asistencia_dict = {
            "id_asistencia": asistencia.id_asistencia,
            "id_estudiante": asistencia.id_estudiante,
            "id_materia": asistencia.id_materia,
            "nombre_materia": nombre_materia,
            "fecha": asistencia.fecha,
            "estado": asistencia.estado,
            "comentario": asistencia.comentario
        }
        asistencias_con_materia.append(asistencia_dict)
    
    return asistencias_con_materia



def get_padres(db: Session, skip: int = 0, limit: int = 100) -> List[Usuario]:
    return db.query(Usuario).filter(Usuario.rol == "padre").offset(skip).limit(limit).all()


def get_padres_with_hijos(db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Obtener lista de padres con sus hijos asociados.
    """
    padres = get_padres(db, skip, limit)
    resultado = []
    
    for padre in padres:
        # Obtener los hijos asociados a este padre
        hijos = get_hijos_por_padre(db, padre.id_usuario)
        
        # Crear un diccionario con la información del padre y sus hijos
        padre_dict = {
            "id_usuario": padre.id_usuario,
            "nombre": padre.nombre,
            "correo": padre.correo,
            "activo": padre.activo,
            "foto": padre.foto,
            "rol": padre.rol,
            "hijos": [{
                "id_estudiante": hijo.id_estudiante,
                "nombre": hijo.nombre
            } for hijo in hijos]
        }
        
        resultado.append(padre_dict)
    
    return resultado


def get_padre_por_id(db: Session, id_padre: UUID) -> Optional[Usuario]:
    return db.query(Usuario).filter(
        Usuario.id_usuario == id_padre,
        Usuario.rol == "padre"
    ).first()


def get_padre_por_correo(db: Session, correo: str) -> Optional[Usuario]:
    return db.query(Usuario).filter(
        Usuario.correo == correo,
        Usuario.rol == "padre"
    ).first()


def actualizar_padre(db: Session, id_padre: UUID, nombre: Optional[str] = None, 
                     correo: Optional[str] = None, activo: Optional[bool] = None, 
                     foto: Optional[str] = None) -> Tuple[Optional[Usuario], bool, str]:
    try:
        padre = get_padre_por_id(db, id_padre)
        if not padre:
            return None, False, "Padre no encontrado"
        
        if correo and correo != padre.correo:
            usuario_existente = db.query(Usuario).filter(Usuario.correo == correo).first()
            if usuario_existente and usuario_existente.id_usuario != id_padre:
                return padre, False, "El correo electrónico ya está en uso por otro usuario"
        
        if nombre is not None:
            padre.nombre = nombre
        
        if correo is not None:
            padre.correo = correo
        
        if activo is not None:
            padre.activo = activo
        
        if foto is not None:
            padre.foto = foto
        
        db.commit()
        db.refresh(padre)
        
        return padre, True, "Datos actualizados correctamente"
    except Exception as e:
        db.rollback()
        return None, False, f"Error al actualizar: {str(e)}"


def eliminar_padre(db: Session, id_padre: UUID) -> Tuple[bool, str]:
    try:
        padre = get_padre_por_id(db, id_padre)
        if not padre:
            return False, "Padre no encontrado"
        
        estudiantes = get_hijos_por_padre(db, id_padre)
        
        for estudiante in estudiantes:
            estudiante.id_padre = None
        
        db.delete(padre)
        db.commit()
        
        return True, "Padre eliminado correctamente"
    except Exception as e:
        db.rollback()
        return False, f"Error al eliminar: {str(e)}"


def cambiar_contrasena_padre(db: Session, id_padre: UUID, contrasena_actual: str, 
                             nueva_contrasena: str) -> Tuple[bool, str]:
    try:
        padre = get_padre_por_id(db, id_padre)
        if not padre:
            return False, "Padre no encontrado"
        
        if not verificar_password(contrasena_actual, padre.contrasena_hash):
            return False, "Contraseña actual incorrecta"
        
        padre.contrasena_hash = hashear_password(nueva_contrasena)
        
        db.commit()
        
        return True, "Contraseña actualizada correctamente"
    except Exception as e:
        db.rollback()
        return False, f"Error al cambiar la contraseña: {str(e)}"
