import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from dotenv import load_dotenv
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class EmailConfig:
    """Configuración para el envío de correos electrónicos."""
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")  
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587")) 
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "")
    FROM_NAME: str = os.getenv("FROM_NAME", "Escuela Manuela Santamaría")
    WEBSITE_URL: str = os.getenv("WEBSITE_URL", "http://localhost:5173")
    
    DEV_MODE: bool = os.getenv("DEV_MODE", "True").lower() in ["true", "1", "t", "y", "yes"]



async def send_email(to_email: str,subject: str,html_content: str,
cc: Optional[List[str]] = None,bcc: Optional[List[str]] = None) -> bool:

    if not all([EmailConfig.SMTP_USER, EmailConfig.SMTP_PASSWORD, EmailConfig.FROM_EMAIL]):
        logger.warning("Configuración SMTP incompleta. Verifica las variables de entorno.")
        return False
    
    if EmailConfig.DEV_MODE is True:
        text_content = re.sub('<.*?>', ' ', html_content)
        text_content = re.sub('\s+', ' ', text_content).strip()
        print(f"DevMode: {EmailConfig.DEV_MODE}")
        print("\n" + "=" * 80)
        print("SIMULACIÓN DE ENVÍO DE CORREO")
        print("=" * 80)
        print(f"De: {EmailConfig.FROM_NAME} <{EmailConfig.FROM_EMAIL}>")
        print(f"Para: {to_email}")
        if cc:
            print(f"CC: {', '.join(cc)}")
        if bcc:
            print(f"BCC: {', '.join(bcc)}")
        print(f"Asunto: {subject}")
        print("-" * 80)
        print("Contenido (primeros 300 caracteres):")
        print(text_content[:300] + "..." if len(text_content) > 300 else text_content)
        print("-" * 80)
        print("NOTA: Este es un envío simulado para desarrollo. Configura DEV_MODE=False para envíos reales.")
        print("=" * 80 + "\n")
        return True
    
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{EmailConfig.FROM_NAME} <{EmailConfig.FROM_EMAIL}>"
        message["To"] = to_email
        
        if cc:
            message["Cc"] = ", ".join(cc)
        
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        server = smtplib.SMTP(EmailConfig.SMTP_SERVER, EmailConfig.SMTP_PORT)
        server.starttls()
        server.login(EmailConfig.SMTP_USER, EmailConfig.SMTP_PASSWORD)
        
        recipients = [to_email]
        if cc:
            recipients.extend(cc)
        if bcc:
            recipients.extend(bcc)
            
        server.sendmail(EmailConfig.FROM_EMAIL, recipients, message.as_string())
        server.quit()
        
        logger.info(f"Correo enviado exitosamente a {to_email}")
        return True
    except Exception as e:
        logger.error(f"Error al enviar correo: {e}")
        return False

async def send_welcome_email(to_email: str, nombre: str, password: str) -> bool:
    print("\n" + "!" * 80)
    print(f"CREDENCIALES PARA {nombre.upper()} ({to_email})")
    print("!" * 80)
    print(f"Contraseña generada: {password}")
    print("IMPORTANTE: Se recomienda cambiar esta contraseña en el primer inicio de sesión.")
    print("!" * 80 + "\n")
    subject = "Bienvenido/a a la Escuela Manuela Santamaría"
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }}
            .header {{
                background-color: #1e2a38;
                color: white;
                padding: 10px 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                padding: 20px;
            }}
            .credentials {{
                background-color: #f9f9f9;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .button {{
                display: inline-block;
                background-color: #1e2a38;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }}
            .footer {{
                margin-top: 30px;
                text-align: center;
                font-size: 0.8em;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Escuela Manuela Santamaría</h1>
            </div>
            <div class="content">
                <h2>¡Bienvenido/a, {nombre}!</h2>
                <p>Se ha creado una cuenta para ti en el sistema de la Escuela Manuela Santamaría.</p>
                
                <div class="credentials">
                    <p><strong>Correo electrónico:</strong> {to_email}</p>
                    <p><strong>Contraseña temporal:</strong> {password}</p>
                </div>
                
                <p>Te recomendamos cambiar tu contraseña la primera vez que inicies sesión.</p>
                
                <p>Para acceder al sistema, haz clic en el siguiente enlace:</p>
                <a href="{EmailConfig.WEBSITE_URL}" class="button">Acceder al Portal</a>
                
                <p>Si tienes alguna pregunta, no dudes en contactar a la administración de la escuela.</p>
            </div>
            <div class="footer">
                <p>Este es un correo automático, por favor no responder.</p>
                <p>© {2025} Escuela Manuela Santamaría. Todos los derechos reservados.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return await send_email(to_email, subject, html_content)


async def send_recovery_password_email(to_email: str, nombre: str, password: str) -> bool:
    """
    Envía un correo electrónico con la nueva contraseña generada para recuperación.
    
    Args:
        to_email: Correo electrónico del destinatario
        nombre: Nombre del usuario
        password: Nueva contraseña generada
        
    Returns:
        True si el correo se envió correctamente, False en caso contrario
    """
    print("\n" + "!" * 80)
    print(f"RECUPERACIÓN DE CONTRASEÑA PARA {nombre.upper()} ({to_email})")
    print("!" * 80)
    print(f"Nueva contraseña: {password}")
    print("IMPORTANTE: Se recomienda cambiar esta contraseña en el primer inicio de sesión.")
    print("!" * 80 + "\n")
    
    subject = "Recuperación de contraseña - Escuela Manuela Santamaría"
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }}
            .header {{
                background-color: #1e2a38;
                color: white;
                padding: 10px 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                padding: 20px;
            }}
            .credentials {{
                background-color: #f9f9f9;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border-left: 4px solid #e74c3c;
            }}
            .button {{
                display: inline-block;
                background-color: #1e2a38;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }}
            .footer {{
                margin-top: 30px;
                text-align: center;
                font-size: 0.8em;
                color: #666;
            }}
            .alert {{
                color: #e74c3c;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Escuela Manuela Santamaría</h1>
            </div>
            <div class="content">
                <h2>Recuperación de contraseña</h2>
                <p>Hola {nombre},</p>
                
                <p>Has solicitado recuperar tu contraseña para acceder al sistema de la Escuela Manuela Santamaría. A continuación, encontrarás tu nueva contraseña temporal:</p>
                
                <div class="credentials">
                    <p><strong>Correo electrónico:</strong> {to_email}</p>
                    <p><strong>Nueva contraseña:</strong> {password}</p>
                </div>
                
                <p class="alert">IMPORTANTE: Por motivos de seguridad, te recomendamos cambiar esta contraseña en cuanto inicies sesión.</p>
                
                <p>Para acceder al sistema, haz clic en el siguiente enlace:</p>
                <a href="{EmailConfig.WEBSITE_URL}" class="button">Iniciar sesión</a>
                
                <p>Si no has solicitado recuperar tu contraseña, por favor contacta inmediatamente a la administración de la escuela.</p>
                
                <p>Saludos cordiales,<br>
                Escuela Manuela Santamaría</p>
            </div>
            <div class="footer">
                <p>Este es un correo automático, por favor no responder.</p>
                <p>© {2025} Escuela Manuela Santamaría. Todos los derechos reservados.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return await send_email(to_email, subject, html_content)