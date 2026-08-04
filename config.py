import os
import urllib.parse
from db import Database

# 1. DEBES DEFINIR LA VARIABLE PRIMERO
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
PROJECT_REF = os.getenv("PROJECT_REF")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# 2. LUEGO HACES LA COMPROBACIÓN
if SUPABASE_DB_URL:
    dsn = SUPABASE_DB_URL
elif PROJECT_REF and DB_PASSWORD:
    password_escaped = urllib.parse.quote_plus(str(DB_PASSWORD))
    dsn = f"postgresql://postgres:{password_escaped}@db.{PROJECT_REF}.supabase.co:5432/postgres"
else:
    raise ValueError(
        "Falta configurar la variable de entorno SUPABASE_DB_URL "
        "o las variables PROJECT_REF y DB_PASSWORD."
    )

# 3. CONEXIÓN A LA BASE DE DATOS
db = Database(dsn)

# 4. CONFIGURACIONES DE MERCADO LIBRE
SITE_ID = os.getenv("SITE_ID", "MLA")
CATEGORY_IDS = [c.strip() for c in os.getenv("CATEGORY_IDS", "").split(",") if c.strip()]
MAX_ITEMS_PER_CATEGORY = int(os.getenv("MAX_ITEMS_PER_CATEGORY", "200"))
