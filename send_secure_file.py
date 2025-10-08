import os
import base64
import hashlib
import zipfile
import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import paramiko
from dotenv import load_dotenv

# ==============================
# 1. CARGA DE VARIABLES
# ==============================
load_dotenv()
SOURCE_FILE = os.getenv("SOURCE_FILE")
AES_KEY = os.getenv("AES_KEY").encode()
SFTP_HOST = os.getenv("SFTP_HOST")
SFTP_PORT = int(os.getenv("SFTP_PORT"))
SFTP_USER = os.getenv("SFTP_USER")
SFTP_KEY = os.getenv("SFTP_KEY")
DESTINATION_DIR = os.getenv("DESTINATION_DIR")
OUTPUT_DIR = "output/"
LOG_DIR = "logs/"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# ==============================
# 2. FUNCIONES AUXILIARES
# ==============================
def generate_hash(file_path):
    """Genera hash SHA-256 del archivo"""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def encrypt_file(input_path, key):
    """Cifra el archivo con AES-256-GCM"""
    with open(input_path, "rb") as f:
        data = f.read()

    # Codificación Base64 previa
    b64_data = base64.b64encode(data)

    # Generar IV aleatorio (12 bytes recomendado)
    iv = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(iv, b64_data, None)

    # Guardar archivo cifrado
    encrypted_path = os.path.join(OUTPUT_DIR, "encrypted_data.bin")
    with open(encrypted_path, "wb") as ef:
        ef.write(iv + ciphertext)
    return encrypted_path

def compress_file(file_path):
    """Comprime el archivo cifrado en ZIP"""
    zip_path = os.path.join(OUTPUT_DIR, "secure_data.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(file_path, os.path.basename(file_path))
    return zip_path

def send_via_sftp(zip_path):
    """Transfiere el archivo cifrado por canal seguro (SFTP sobre SSH)"""
    key = paramiko.RSAKey.from_private_key_file(SFTP_KEY)
    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USER, pkey=key)
    sftp = paramiko.SFTPClient.from_transport(transport)
    remote_path = os.path.join(DESTINATION_DIR, os.path.basename(zip_path))
    sftp.put(zip_path, remote_path)
    sftp.close()
    transport.close()

def write_log(entry):
    """Registra el evento en bitácora"""
    log_file = os.path.join(LOG_DIR, f"log_{datetime.date.today()}.txt")
    with open(log_file, "a") as lf:
        lf.write(entry + "\n")

# ==============================
# 3. FLUJO PRINCIPAL
# ==============================
if __name__ == "__main__":
    print("=== Iniciando envío seguro ESICORP ===")
    try:
        # Paso 1: Generar hash original
        original_hash = generate_hash(SOURCE_FILE)

        # Paso 2: Cifrar y codificar
        encrypted_file = encrypt_file(SOURCE_FILE, AES_KEY)

        # Paso 3: Comprimir
        zip_file = compress_file(encrypted_file)

        # Paso 4: Enviar
        send_via_sftp(zip_file)

        # Paso 5: Registrar log
        log_entry = f"[{datetime.datetime.now()}] Archivo: {os.path.basename(SOURCE_FILE)} | Hash: {original_hash} | Destino: {SFTP_HOST}"
        write_log(log_entry)

        print("✅ Envío completado exitosamente.")
    except Exception as e:
        error_msg = f"[{datetime.datetime.now()}] ERROR: {str(e)}"
        write_log(error_msg)
        print("❌ Error en el proceso:", e)
