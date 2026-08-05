import os
import urllib.parse
from db import Database

# 1. DEBES DEFINIR LA VARIABLE PRIMERO
DB_HOST = "aws-0-ca-central-1.pooler.supabase.com"
DB_NAME = "postgres"
# Unificado con app.py: usamos las mismas variables de entorno (BASE_USER / BASE_PASS)
# para no tener credenciales duplicadas en Railway.
DB_USER = os.environ.get("BASE_USER") or os.environ.get("USER_BASE")
DB_PASS = os.environ.get("BASE_PASS") or os.environ.get("CLAVE_BASE")
DB_PORT = "6543"

# 3. CONEXIÓN A LA BASE DE DATOS
db = psycopg2.connect(
        host=DB_HOST, database=DB_NAME,
        user=DB_USER, password=DB_PASS, port=DB_PORT,
        connect_timeout=10,
        sslmode="require",
        options="-c search_path=public --project=vlndghikrjvxmiibbqbo"
    )

# 4. CONFIGURACIONES DE MERCADO LIBRE
SITE_ID = os.getenv("SITE_ID", "MLA")
CATEGORY_IDS = [c.strip() for c in os.getenv("CATEGORY_IDS", "").split(",") if c.strip()]
MAX_ITEMS_PER_CATEGORY = int(os.getenv("MAX_ITEMS_PER_CATEGORY", "200"))
