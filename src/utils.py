import sys
import os
import shutil
import psycopg2
import urllib.parse

# ======================================================
#  CONFIGURACIÓN DE SUPABASE (POSTGRESQL)
# ======================================================
# 1. Tu contraseña (¡ASEGÚRATE DE QUE ESTÉ BIEN ESCRITA!)
RAW_PASSWORD = "10Chocolates@" 

# 2. Configuración del Servidor
# CAMBIO CLAVE: Cambiamos el puerto 5432 por 6543 (Pooler)
# Esto ayuda a saltarse bloqueos de firewall y problemas de IPv6
HOST_STRING = "postgres@db.wskrvdxmugddtyeikeyx.supabase.co:6543/postgres"

# 3. Construcción segura de la URL (No tocar)
encoded_pass = urllib.parse.quote_plus(RAW_PASSWORD)
user_part, rest_of_host = HOST_STRING.split("@", 1)

# Agregamos '?sslmode=require' para forzar una conexión segura y evitar rechazos
DB_URI = f"postgresql://{user_part}:{encoded_pass}@{rest_of_host}?sslmode=require"

# ======================================================
#  CONFIGURACIÓN DE VERSIONES (AUTO-UPDATE)
# ======================================================
CURRENT_VERSION = "1.0"
UPDATE_URL = "https://raw.githubusercontent.com/nsegurag/LabelGenerator/refs/heads/main/version.txt"
RELEASE_URL = "https://github.com/nsegurag/LabelGenerator/releases/latest"

def resource_path(relative_path):
    """Obtiene ruta absoluta para recursos dentro del exe"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)

def get_user_data_dir():
    """Ruta segura en AppData"""
    path = os.path.join(os.getenv('LOCALAPPDATA'), 'LabelGenerator')
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def get_db_connection():
    """
    Crea la conexión a la nube.
    """
    try:
        conn = psycopg2.connect(DB_URI)
        return conn
    except Exception as e:
        print(f"❌ Error conectando a Supabase: {e}")
        # Si falla, relanzamos el error para que la interfaz muestre el mensaje
        raise e