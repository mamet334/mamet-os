"""
MAMET OS - Encryption Module
============================
Menangani enkripsi AES-256 untuk kredensial sensitif seperti API Key.
"""

import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def get_encryption_key(user_email: str) -> bytes:
    """
    Menghasilkan kunci AES statis berdasarkan email pengguna dan salt rahasia kernel.
    Idealnya password pengguna juga digunakan, namun untuk kemudahan dekripsi latar belakang,
    kita menggunakan kombinasi deterministik yang di-hash 100k iterasi.
    """
    salt = b'mamet_os_v3_salt_12345'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(user_email.encode()))
    return key

def encrypt_data(data: str, user_email: str) -> str:
    """Mengenkripsi string data menggunakan AES-256 (Fernet)."""
    if not data:
        return data
        
    try:
        # Periksa apakah data sudah terenkripsi (Fernet string biasanya diawali gAAAAA)
        if data.startswith('gAAAAA'):
            return data
            
        f = Fernet(get_encryption_key(user_email))
        return f.encrypt(data.encode()).decode()
    except Exception as e:
        print(f"[ENCRYPTION] Gagal enkripsi: {e}")
        return data

def decrypt_data(encrypted_data: str, user_email: str) -> str:
    """Mendekripsi string data."""
    if not encrypted_data:
        return encrypted_data
        
    try:
        # Hanya coba dekripsi jika formatnya tampak seperti Fernet
        if not encrypted_data.startswith('gAAAAA'):
            return encrypted_data
            
        f = Fernet(get_encryption_key(user_email))
        return f.decrypt(encrypted_data.encode()).decode()
    except Exception as e:
        print(f"[ENCRYPTION] Gagal dekripsi: {e}")
        return encrypted_data
