import os
import urllib.parse
from db import Database

# 1. Obtención de variables de entorno con valores por defecto seguros
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
PROJECT_REF = os.getenv("PROJECT_REF")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# 2. Construcción segura de la cadena de conexión (DSN)
if SUPABASE_DB_URL:
    dsn = SUPABASE_DB_URL
elif PROJECT_REF and DB_PASSWORD:
    # Convertir explícitamente a str evita el fallo TypeError: expected bytes
    password_escaped = urllib.parse.quote_plus(str(DB_PASSWORD))
    
    # OPCIÓN DIRECTA (Puerto 5432):
    dsn = f"postgresql://postgres:{password_escaped}@db.{PROJECT_REF}.supabase.co:5432/postgres"
    
    # Si requieres usar el POOLER, usa la siguiente línea en su lugar:
    # dsn = f"postgresql://postgres.{PROJECT_REF}:{password_escaped}@aws-0-ca-central-1.pooler.supabase.com:5432/postgres"
else:
    raise ValueError(
        "ERROR CRÍTICO: Faltan variables de entorno. "
        "Asegúrate de definir 'DB_PASSWORD' y 'PROJECT_REF' (o 'SUPABASE_DB_URL') en tu servidor."
    )

# 3. Inicialización de la base de datos (se ejecuta solo si el DSN es válido)
db = Database(dsn)

# 4. Parámetros de la aplicación Mercado Libre
SITE_ID = os.getenv("SITE_ID", "MLA")
CATEGORY_IDS = [c.strip() for c in os.getenv("CATEGORY_IDS", "").split(",") if c.strip()]
MAX_ITEMS_PER_CATEGORY = int(os.getenv("MAX_ITEMS_PER_CATEGORY", "200"))
