from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import random
import string
from passlib.context import CryptContext
from app.modules.usuarios.models import Profesor, Usuario
from app.modules.materias.models_profesor_materia import ProfesorMateria
from app.modules.secciones.models_profesor_seccion import ProfesorSeccion
from app.modules.materias.models import Materia
from app.modules.secciones.models import Seccion
from app.modules.anio_lectivo.models import AnioLectivo
from sqlalchemy import and_

# Para encriptar contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def obtener_profesores(db: Session):
    """Obtiene todos los profesores con información básica"""
    try:
        # Obtener todos los usuarios con rol profesor
        usuarios = db.query(Usuario).filter(Usuario.rol == "profesor").all()
        
        # Convertir los usuarios a un formato que FastAPI pueda serializar
        profesores = []
        for usuario in usuarios:
            profesor = {
                "id_profesor": str(usuario.id_usuario),  # Convertir UUID a string
                "nombre": usuario.nombre,
                "correo": usuario.correo
            }
            profesores.append(profesor)
        
        return profesores
    except Exception as e:
        print(f"Error en obtener_profesores: {e}")
        # En caso de error, devolver una lista vacía en lugar de propagar el error
        return []


def obtener_profesor_por_id(db: Session, id_profesor: uuid.UUID):
    """Obtiene un profesor por su ID"""
    try:
        usuario = db.query(Usuario).filter(and_(Usuario.id_usuario == id_profesor, Usuario.rol == "profesor")).first()
        
        if not usuario:
            return None
        
        # Mapear los campos del modelo Usuario al esquema ProfesorBase
        return {
            "id_profesor": str(usuario.id_usuario),  # Convertir UUID a string
            "nombre": usuario.nombre,
            "correo": usuario.correo
        }
    except Exception as e:
        print(f"Error en obtener_profesor_por_id: {e}")
        return None


def obtener_materias_profesor(db: Session, id_profesor: uuid.UUID, id_anio: Optional[uuid.UUID] = None):
    """Obtiene todas las materias asignadas a un profesor"""
    query = db.query(
        Materia.id_materia,
        Materia.nombre,
        AnioLectivo.id_anio,
        AnioLectivo.nombre.label("anio_nombre")
    ).join(
        ProfesorMateria, Materia.id_materia == ProfesorMateria.id_materia
    ).join(
        AnioLectivo, ProfesorMateria.id_anio == AnioLectivo.id_anio
    ).filter(
        ProfesorMateria.id_profesor == id_profesor
    )
    
    if id_anio:
        query = query.filter(ProfesorMateria.id_anio == id_anio)
    
    # Convertir las tuplas en diccionarios
    results = query.all()
    materias = [
        {
            "id_materia": materia[0],
            "nombre": materia[1],
            "id_anio": materia[2],
            "anio_nombre": materia[3]
        }
        for materia in results
    ]
    
    return materias


def obtener_secciones_profesor(db: Session, id_profesor: uuid.UUID):
    """Obtiene todas las secciones asignadas a un profesor"""
    results = db.query(
        Seccion.id_seccion,
        Seccion.nombre,
        Seccion.grado,
        AnioLectivo.nombre.label("anio_nombre")
    ).join(
        ProfesorSeccion, Seccion.id_seccion == ProfesorSeccion.id_seccion
    ).join(
        AnioLectivo, Seccion.id_anio == AnioLectivo.id_anio
    ).filter(
        ProfesorSeccion.id_profesor == id_profesor
    ).all()
    
    # Convertir las tuplas en diccionarios
    secciones = [
        {
            "id_seccion": seccion[0],
            "nombre": seccion[1],
            "grado": seccion[2],
            "anio_nombre": seccion[3]
        }
        for seccion in results
    ]
    
    return secciones


def asignar_materias_profesor(db: Session, id_profesor: uuid.UUID, id_materias: List[uuid.UUID], id_anio: uuid.UUID):
    """Asigna materias a un profesor para un año lectivo específico"""
    try:
        # Verificar que el profesor exista
        profesor = db.query(Usuario).filter(
            and_(Usuario.id_usuario == id_profesor, Usuario.rol == "profesor")
        ).first()
        
        if not profesor:
            print(f"Error: Profesor con ID {id_profesor} no encontrado")
            return False
            
        # Primero eliminamos asignaciones existentes para este profesor y año
        db.query(ProfesorMateria).filter(
            and_(
                ProfesorMateria.id_profesor == id_profesor,
                ProfesorMateria.id_anio == id_anio
            )
        ).delete(synchronize_session=False)
        
        # Luego creamos las nuevas asignaciones
        for id_materia in id_materias:
            # Verificar que la materia exista
            materia = db.query(Materia).filter(Materia.id_materia == id_materia).first()
            if not materia:
                print(f"Error: Materia con ID {id_materia} no encontrada")
                continue
                
            asignacion = ProfesorMateria(
                id_profesor=id_profesor,
                id_materia=id_materia,
                id_anio=id_anio
            )
            db.add(asignacion)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error en asignar_materias_profesor: {e}")
        return False


def asignar_secciones_profesor(db: Session, id_profesor: uuid.UUID, id_secciones: List[uuid.UUID]):
    """Asigna secciones a un profesor"""
    try:
        # Verificar que el profesor exista
        profesor = db.query(Usuario).filter(
            and_(Usuario.id_usuario == id_profesor, Usuario.rol == "profesor")
        ).first()
        
        if not profesor:
            print(f"Error: Profesor con ID {id_profesor} no encontrado")
            return False
            
        # Primero eliminamos asignaciones existentes para este profesor
        db.query(ProfesorSeccion).filter(ProfesorSeccion.id_profesor == id_profesor).delete(synchronize_session=False)
        
        # Luego creamos las nuevas asignaciones
        for id_seccion in id_secciones:
            # Verificar que la sección exista
            seccion = db.query(Seccion).filter(Seccion.id_seccion == id_seccion).first()
            if not seccion:
                print(f"Error: Sección con ID {id_seccion} no encontrada")
                continue
                
            asignacion = ProfesorSeccion(
                id_profesor=id_profesor,
                id_seccion=id_seccion
            )
            db.add(asignacion)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error en asignar_secciones_profesor: {e}")
        return False


def crear_profesor(db: Session, nombre: str, correo: str):
    """Crea un nuevo profesor y un usuario con rol de profesor"""
    try:
        # Generar contraseña aleatoria
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        # Crear usuario con rol profesor
        nuevo_usuario = Usuario(
            nombre=nombre,
            correo=correo,
            rol="profesor",
            contrasena_hash=pwd_context.hash(password)
        )
        db.add(nuevo_usuario)
        db.flush()  # Para obtener el id_usuario generado
        
        # Crear registro en la tabla profesor
        from app.modules.usuarios.models import Profesor
        nuevo_profesor = Profesor(id_profesor=nuevo_usuario.id_usuario)
        db.add(nuevo_profesor)
        
        db.commit()
        db.refresh(nuevo_usuario)
        
        return {
            "id_profesor": nuevo_usuario.id_usuario,
            "nombre": nuevo_usuario.nombre,
            "correo": nuevo_usuario.correo,
            "password": password
        }
    except Exception as e:
        db.rollback()
        print(f"Error en crear_profesor: {e}")
        raise e


def eliminar_profesor(db: Session, id_profesor: uuid.UUID):
    """Elimina un profesor y su usuario asociado"""
    try:
        # Primero verificamos que exista y sea un profesor
        usuario = db.query(Usuario).filter(
            and_(Usuario.id_usuario == id_profesor, Usuario.rol == "profesor")
        ).first()
        
        if not usuario:
            print(f"Error: Usuario con ID {id_profesor} no encontrado o no es profesor")
            return False
        
        # Gracias a la configuración de cascade="all, delete-orphan" en el modelo,
        # al eliminar el usuario también se eliminará automáticamente el registro en la tabla profesor
        db.delete(usuario)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error en eliminar_profesor: {e}")
        return False


def actualizar_profesor(db: Session, id_profesor: uuid.UUID, nombre: str, correo: str):
    """Actualiza los datos de un profesor"""
    try:
        # Verificar que exista el usuario con rol profesor
        usuario = db.query(Usuario).filter(and_(Usuario.id_usuario == id_profesor, Usuario.rol == "profesor")).first()
        
        if not usuario:
            print(f"Error: Usuario con ID {id_profesor} no encontrado o no es profesor")
            return None
        
        # Verificar que exista el registro en la tabla profesor
        from app.modules.usuarios.models import Profesor
        profesor = db.query(Profesor).filter(Profesor.id_profesor == id_profesor).first()
        
        if not profesor:
            print(f"Error: Registro de profesor con ID {id_profesor} no encontrado")
            # Si no existe, lo creamos
            profesor = Profesor(id_profesor=id_profesor)
            db.add(profesor)
        
        # Verificar si el correo ya existe en otro usuario
        if correo != usuario.correo:
            usuario_existente = db.query(Usuario).filter(and_(Usuario.correo == correo, Usuario.id_usuario != id_profesor)).first()
            if usuario_existente:
                print(f"Error: Ya existe otro usuario con el correo {correo}")
                return None
        
        # Actualizamos los datos
        usuario.nombre = nombre
        usuario.correo = correo
        
        db.commit()
        db.refresh(usuario)
        
        return {
            "id_profesor": str(usuario.id_usuario),  # Convertir UUID a string
            "nombre": usuario.nombre,
            "correo": usuario.correo
        }
    except Exception as e:
        db.rollback()
        print(f"Error en actualizar_profesor: {e}")
        return None


def obtener_profesor_completo(db: Session, id_profesor: uuid.UUID):
    """Obtiene un profesor con todas sus materias y secciones asignadas"""
    profesor = obtener_profesor_por_id(db, id_profesor)
    if not profesor:
        return None
    
    materias = obtener_materias_profesor(db, id_profesor)
    secciones = obtener_secciones_profesor(db, id_profesor)
    
    return {
        "id_profesor": profesor["id_profesor"],
        "nombre": profesor["nombre"],
        "correo": profesor["correo"],
        "materias": materias,
        "secciones": secciones
    }
