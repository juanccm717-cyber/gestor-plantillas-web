import bcrypt
password = 'test125879'
hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
hashed_str = hashed_bytes.decode('utf-8')
print("Copia y pega este hash en Supabase para el usuario 'admin':")
print(hashed_str)
