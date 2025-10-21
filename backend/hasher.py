import bcrypt
import os

# Contraseña en texto plano. Se codifica antes de hashear.
password_plano = "password123"

# Genera una sal (salt) para seguridad.
salt = bcrypt.gensalt(rounds=12) # Usa la misma fuerza que tu passlib (round 12)

# Genera el hash.
hashed_password = bcrypt.hashpw(password_plano.encode('utf-8'), salt)

print("-" * 50)
print(f"Contraseña en texto plano: {password_plano}")
# Decodifica el hash a una cadena para que puedas copiarlo.
print(f"HASH DE BCRYPT (Copia ESTE valor en Supabase):")
print(hashed_password.decode('utf-8'))
print("-" * 50)