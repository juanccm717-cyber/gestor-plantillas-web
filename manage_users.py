import os
from sqlalchemy import create_engine, text
from getpass import getpass
import scrypt

# Carga la URL de la base de datos desde el archivo .env
# Asegúrate de tener un archivo .env con tu DATABASE_URL
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("No se encontró la variable de entorno DATABASE_URL. Asegúrate de que tu archivo .env está configurado.")

engine = create_engine(DATABASE_URL)

def add_user():
    """Añade un nuevo usuario a la base de datos de forma interactiva y segura."""
    print("--- Añadir Nuevo Usuario ---")
    username = input("Introduce el nombre de usuario: ")
    password = getpass("Introduce la contraseña: ")
    password_confirm = getpass("Confirma la contraseña: ")

    if password != password_confirm:
        print("\n[ERROR] Las contraseñas no coinciden. Operación cancelada.")
        return

    # Hashear la contraseña con scrypt
    print("Hasheando contraseña...")
    hashed_password = scrypt.hash(password, salt=os.urandom(16)).hex()
    
    role = input("Introduce el rol (ej: administrador, usuario): ")

    try:
        with engine.connect() as connection:
            # Verificar si el usuario ya existe
            check_sql = text("SELECT id FROM usuarios WHERE username = :username")
            existing_user = connection.execute(check_sql, {'username': username}).first()
            
            if existing_user:
                print(f"\n[ERROR] El usuario '{username}' ya existe. Operación cancelada.")
                return

            # Insertar el nuevo usuario
            insert_sql = text("""
                INSERT INTO usuarios (username, password_hash, role) 
                VALUES (:username, :password_hash, :role)
            """)
            connection.execute(insert_sql, {
                'username': username,
                'password_hash': hashed_password,
                'role': role
            })
            # Es necesario hacer commit para que los cambios se guarden
            connection.commit()
        
        print(f"\n¡Éxito! Usuario '{username}' con rol '{role}' ha sido añadido a la base de datos.")

    except Exception as e:
        print(f"\n[ERROR] Ocurrió un error al conectar o insertar en la base de datos: {e}")

if __name__ == "__main__":
    add_user()

