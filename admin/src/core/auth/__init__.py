from src.core.database import db
from src.core.auth.user import User
import bcrypt

def list_users():
    return db.session.query(User).all()

def verify_password(password: str, hashed) -> bool:
    try:
        print(f"Verifying password:")
        print(f"  Password (plain): {password}")
        print(f"  Hashed password type: {type(hashed)}")
        print(f"  Hashed password: {hashed}")
        
        # Si es un string que viene de PostgreSQL (formato \x...)
        if isinstance(hashed, str) and hashed.startswith('\\x'):
            print("  Converting hex string to bytes")
            # Quitar el \x y convertir hex a bytes
            hashed = bytes.fromhex(hashed[2:])
        elif isinstance(hashed, str):
            print("  Warning: Hashed password is string, converting to bytes")
            hashed = hashed.encode('utf-8')
        
        print(f"  Final hashed password (bytes): {hashed}")
        result = bcrypt.checkpw(password.encode('utf-8'), hashed)
        print(f"  Verification result: {result}")
        return result
    except Exception as e:
        print(f"  Error during verification: {e}")
        return False

def find_user(email, password):
    from core.models.User import User

    print(f"Finding user with email: {email}")
    user = User.query.filter_by(email=email).first()
    print(f"User found: {user}")
    print(f"Password provided: {password}")
    
    if user:
        print(f"Stored hashed password: {user.password}")
        print(f"Stored password type: {type(user.password)}")
        
        if verify_password(password, user.password):
            print("Password verification successful!")
            return user
        else:
            print("Password verification failed!")
    else:
        print('No user found with that email')
    
    return None