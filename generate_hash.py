from passlib.context import CryptContext

# Configurar contexto con Argon2 (sin limite de longitud) y Bcrypt como fallback
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

if __name__ == "__main__":
    print("="*60)
    print("GENERADOR DE HASH ARGON2")
    print("="*60)
    
    password = input("Ingresa la contraseña a hashear: ")
    
    if password:
        hashed = hash_password(password)
        print("\n✅ Hash generado exitosamente:")
        print("-" * 20)
        print(hashed)
        print("-" * 20)
        print(f"\nLongitud del hash: {len(hashed)} caracteres")
        print("\nInstrucciones:")
        print("1. Copia este hash.")
        print("2. Pégalo en la columna 'passwordHash' de tu tabla 'tab_usuario' en la BD.")
        print("3. Intenta loguearte de nuevo usando la contraseña original.")
    else:
        print("❌ No ingresaste ninguna contraseña.")
