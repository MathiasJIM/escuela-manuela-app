import random
import string
import re
import unicodedata
from typing import Optional


def generar_contrasena_segura(correo: str, nombre: Optional[str] = None) -> str:
    username = correo.split('@')[0]
    
    username_clean = re.sub(r'[^a-zA-Z0-9]', '', username)
    
    if len(username_clean) < 3 and nombre:
        nombre_clean = re.sub(r'[^a-zA-Z0-9]', '', nombre)
        username_clean = nombre_clean[:3] if len(nombre_clean) >= 3 else nombre_clean
    
    base = username_clean[:5]
    
    if base:
        pos = random.randint(0, len(base) - 1)
        base = base[:pos] + base[pos].upper() + base[pos+1:]
    
    num = str(random.randint(10, 9999))
    
    special_chars = '!@#$%^&*'
    special = random.choice(special_chars)
    
    random_letters = ''.join(random.choices(string.ascii_letters, k=2))
    
    all_parts = [base, num, special, random_letters]
    random.shuffle(all_parts)
    password = ''.join(all_parts)
    
    while len(password) < 8:
        password += random.choice(string.ascii_letters + string.digits)
    
    return password


def validar_fortaleza_contrasena(contrasena: str) -> bool:
    if len(contrasena) < 8:
        return False
    
    if not re.search(r'[A-Z]', contrasena):
        return False
    
    if not re.search(r'[0-9]', contrasena):
        return False
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', contrasena):
        return False
    
    return True


def generar_correo_padre(nombre_estudiante: str, db) -> str:
    from app.modules.usuarios.models import Usuario
    
    nombre_normalizado = ''.join(
        c for c in unicodedata.normalize('NFD', nombre_estudiante.lower())
        if not unicodedata.combining(c)
    )
    
    nombre_normalizado = re.sub(r'[^a-z0-9]', ' ', nombre_normalizado)
    
    partes = nombre_normalizado.split()
    
    if len(partes) >= 2:
        base_usuario = f"{partes[0][0]}{partes[1]}"
    else:
        base_usuario = f"{partes[0][0]}{partes[0]}"
    
    secuencia_random = str(random.randint(1000, 9999))
    
    usuario_base = f"{base_usuario}{secuencia_random}"
    
    usuario = f"{usuario_base}@escmanuela.ed.cr"
    
    intentos = 0
    usuario_original = usuario_base
    
    while db.query(Usuario).filter(Usuario.correo == usuario).first():
        intentos += 1
        secuencia_random = str(random.randint(1000, 9999))
        usuario = f"{usuario_original}{secuencia_random}@escmanuela.ed.cr"
        
        if intentos > 10:
            import time
            timestamp = int(time.time()) % 10000
            usuario = f"{usuario_original}{timestamp}@escmanuela.ed.cr"
            break
    
    return usuario
