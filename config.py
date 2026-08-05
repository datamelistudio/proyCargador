import os
import urllib.parse
import psycopg2

# 1. Parámetros de la base de datos
DB_HOST = "aws-0-ca-central-1.pooler.supabase.com"
DB_NAME = "postgres"
DB_PORT = "6543"
PROJECT_REF = "dlejozthzgnbfbqjuejo"

# 2. Lectura de variables de entorno
RAW_USER = os.environ.get("BASE_USER") or os.environ.get("USER_BASE") or "postgres"
RAW_PASS = os.environ.get("BASE_PASS") or os.environ.get("CLAVE_BASE") or ""

# 3. Formateo correcto para el Pooler de Supabase
# Si el usuario no trae la referencia del proyecto, se la adjuntamos automáticamente:
if "." not in RAW_USER:
    DB_USER = f"{RAW_USER}.{PROJECT_REF}"
else:
    DB_USER = RAW_USER

DB_USER="postgres.dlejozthzgnbfbqjuejo"

# Escapar la contraseña si contiene caracteres especiales
DB_PASS = urllib.parse.quote_plus(RAW_PASS)

print("Usuario usado:", DB_USER)
print("¿Hay contraseña?:", bool(DB_PASS))

# 4. Conexión a la base de datos
db = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user="postgres.dlejozthzgnbfbqjuejo",
    password=RAW_PASS,  # En psycopg2.connect directo pasa la clave tal cual; si usas DSN en URI usa DB_PASS
    port=DB_PORT,
    connect_timeout=10,
    sslmode="require",
    options=f"-c search_path=public --project={PROJECT_REF}"
)

# 5. Configuraciones de Mercado Libre
SITE_ID = os.getenv("SITE_ID", "MLA")
CATEGORY_IDS = [c.strip() for c in os.getenv("CATEGORY_IDS", "").split(",") if c.strip()]
MAX_ITEMS_PER_CATEGORY = int(os.getenv("MAX_ITEMS_PER_CATEGORY", "200"))
