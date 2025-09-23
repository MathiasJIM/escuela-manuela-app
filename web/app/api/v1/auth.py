from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.modules.usuarios.schemas import UsuarioLogin, UsuarioOut, UsuarioCreate, RegistroResponse, CambioContrasenaResponse, CambioContrasenaRequest
from app.modules.usuarios.crud import autenticar_usuario, crear_usuario, obtener_usuario_por_correo, restaurar_contrasena, actualizar_contrasena
from app.db.session import SessionLocal
from app.core.security import crear_token_acceso
from app.core.email import send_welcome_email
from app.api.v1.deps import get_db, get_current_user

router = APIRouter()

@router.post("/login", response_model=dict)
def login(usuario_login: UsuarioLogin, db: Session = Depends(get_db)):
    """Endpoint para autenticar un usuario y obtener un token de acceso.
    
    Retorna el token de acceso y la información básica del usuario para facilitar
    la implementación del frontend.
    """
    usuario = autenticar_usuario(db, usuario_login.correo, usuario_login.contrasena)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    
    access_token = crear_token_acceso({"sub": str(usuario.id_usuario)})
    
    # Incluir información del usuario en la respuesta
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "rol": usuario.rol
    }


@router.get("/me", response_model=UsuarioOut)
def obtener_usuario_actual(usuario_actual = Depends(get_current_user)):
    return usuario_actual


@router.post("/registrar", response_model=RegistroResponse)
async def registrar(usuario_in: UsuarioCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    existente = obtener_usuario_por_correo(db, usuario_in.correo)
    if existente:
        raise HTTPException(status_code=400, detail="Correo ya registrado")
    
    usuario, contrasena_generada = crear_usuario(db, usuario_in)
    
    if usuario.rol in ["profesor", "direccion"] and contrasena_generada and usuario_in.correo:
        background_tasks.add_task(
            send_welcome_email,
            to_email=usuario.correo,
            nombre=usuario.nombre,
            password=contrasena_generada
        )
    
    return {
        "usuario": usuario,
        "contrasena_generada": contrasena_generada
    }


@router.post("/recuperar-contrasena", response_model=dict)
async def recuperar_contrasena(correo: str, db: Session = Depends(get_db)):
    usuario, nueva_contrasena, exito = restaurar_contrasena(db, correo)
    if not exito:
        return {
            "mensaje": "Si el correo existe y pertenece a un usuario válido, se enviará un correo con instrucciones."
        }
    
    try:
        from app.core.email import send_recovery_password_email
        
        resultado = await send_recovery_password_email(
            to_email=usuario.correo,
            nombre=usuario.nombre,
            password=nueva_contrasena
        )
        
        if not resultado:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al enviar el correo de recuperación. Por favor, verifica la configuración SMTP."
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar el correo de recuperación: {str(e)}"
        )
    
    return {
        "mensaje": "Si el correo existe y pertenece a un usuario válido, se enviará un correo con instrucciones."
    }


@router.post("/cambiar-contrasena", response_model=CambioContrasenaResponse)
def cambiar_contrasena(datos: CambioContrasenaRequest, db: Session = Depends(get_db), usuario_actual = Depends(get_current_user)):
    """Endpoint para cambiar la contraseña del usuario autenticado."""
    usuario, exito = actualizar_contrasena(
        session=db,
        usuario_id=usuario_actual.id_usuario,
        contrasena_actual=datos.contrasena_actual,
        nueva_contrasena=datos.nueva_contrasena
    )
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
      
    if not exito:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )
    
    return {
        "mensaje": "Contraseña actualizada correctamente"
    }