import bcrypt

# --- Contraseña para el ADMIN ---
password_admin = 'test125879'
hashed_bytes_admin = bcrypt.hashpw(password_admin.encode('utf-8'), bcrypt.gensalt())
hashed_str_admin = hashed_bytes_admin.decode('utf-8')

# --- Contraseña para el USUARIO ---
password_usuario = 'test1234'
hashed_bytes_usuario = bcrypt.hashpw(password_usuario.encode('utf-8'), bcrypt.gensalt())
hashed_str_usuario = hashed_bytes_usuario.decode('utf-8')

print("\n✅ ¡Hashes generados con éxito!\n")

print("--- Para el usuario 'admin' ---")
print("Copia este hash y pégalo en la columna 'password_hash' de Supabase:\n")
print(hashed_str_admin)
print("------------------------------------------------------------\n")

print("--- Para el usuario 'usuario' ---")
print("Copia este hash y pégalo en la columna 'password_hash' de Supabase:\n")
print(hashed_str_usuario)
print("------------------------------------------------------------\n")
