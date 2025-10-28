import os
from sqlalchemy import create_engine, text
from getpass import getpass
import bcrypt  # <--- CORREGIDO
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("No se encontró la variable de entorno DATABASE_URL.")
engine = create_engine(DATABASE_URL)

def add_user():
    print("--- Añadir Nuevo Usuario (usando bcrypt) ---")
    username = input("Introduce el nombre de usuario: ")
    password = getpass("Introduce la contraseña: ")
    password_confirm = getpass("Confirma la contraseña: ")

    if password != password_confirm:
        print("\n[ERROR] Las contraseñas no coinciden.")
        return

    # --- Lógica de hashing con bcrypt (CORREGIDO) ---
    print("Hasheando contraseña con bcrypt...")
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password_bytes = bcrypt.hashpw(password_bytes, salt)
    hashed_password_hex = hashed_password_bytes.hex()
    
    role = input("Introduce el rol (ej: administrador, usuario): ")

    try:
        with engine.connect() as connection:
            check_sql = text("SELECT id FROM usuarios WHERE username = :username")
            existing_user = connection.execute(check_sql, {'username': username}).first()
            if existing_user:
                print(f"\n[ERROR] El usuario '{username}' ya existe.")
                return

            insert_sql = text("INSERT INTO usuarios (username, password_hash, role) VALUES (:username, :password_hash, :role)")
            connection.execute(insert_sql, {
                'username': username,
                'password_hash': hashed_password_hex,  # <--- Usa el nuevo hash
                'role': role
            })
            connection.commit()
        print(f"\n¡Éxito! Usuario '{username}' con rol '{role}' ha sido añadido a la base de datos.")
    except Exception as e:
        print(f"\n[ERROR] Ocurrió un error: {e}")

if __name__ == "__main__":
    add_user()
