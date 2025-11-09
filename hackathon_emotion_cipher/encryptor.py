# encryptor.py
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import os
import base64

KEYS_DIR = "keys"
PRIVATE_KEY_PATH = os.path.join(KEYS_DIR, "private_key.pem")
PUBLIC_KEY_PATH = os.path.join(KEYS_DIR, "public_key.pem")

# ---------------------------------------------------------------------
# Load or generate RSA keys
# ---------------------------------------------------------------------
def load_rsa_keys():
    if not os.path.exists(PRIVATE_KEY_PATH) or not os.path.exists(PUBLIC_KEY_PATH):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        with open(PRIVATE_KEY_PATH, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()))
        public_key = private_key.public_key()
        with open(PUBLIC_KEY_PATH, "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo))
    else:
        with open(PRIVATE_KEY_PATH, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)
        with open(PUBLIC_KEY_PATH, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())
    return private_key, public_key

# ---------------------------------------------------------------------
# AES Encryption + RSA Key Wrapping
# ---------------------------------------------------------------------
def encrypt_message(message: str):
    try:
        private_key, public_key = load_rsa_keys()

        # Generate AES key and nonce
        aes_key = AESGCM.generate_key(bit_length=128)
        aesgcm = AESGCM(aes_key)
        nonce = os.urandom(12)

        # Encrypt the message
        ciphertext = aesgcm.encrypt(nonce, message.encode('utf-8'), None)
        encrypted_text = base64.b64encode(nonce + ciphertext).decode('utf-8')

        # Encrypt AES key with RSA public key
        encrypted_key = public_key.encrypt(
            aes_key,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
        encrypted_key_b64 = base64.b64encode(encrypted_key).decode('utf-8')

        return encrypted_text, encrypted_key_b64
    except Exception as e:
        print("⚠️ Encryption Error:", e)
        raise e

# ---------------------------------------------------------------------
# AES Decryption + RSA Key Unwrapping
# ---------------------------------------------------------------------
def decrypt_message(encrypted_text: str, encrypted_key_b64: str):
    try:
        private_key, _ = load_rsa_keys()

        # Decode the base64-encoded parts
        encrypted_data = base64.b64decode(encrypted_text)
        nonce, ciphertext = encrypted_data[:12], encrypted_data[12:]
        encrypted_key = base64.b64decode(encrypted_key_b64)

        # Decrypt AES key
        aes_key = private_key.decrypt(
            encrypted_key,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

        # Decrypt message
        aesgcm = AESGCM(aes_key)
        decrypted_text = aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
        return decrypted_text
    except Exception as e:
        print("⚠️ Decryption Error:", e)
        raise e
