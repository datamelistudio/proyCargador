import os
import urllib.parse
from db import Database

# Cadena de conexión a la base Postgres de Supabase.
# Usar la connection string "directa" (puerto 5432), no el pooler,
# ya que este servicio corre una vez al día y no necesita pooling.
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")

PROJECT_REF = os.getenv("PROJECT_REF")    # Tu ID de proyecto
DB_PASSWORD = os.getenv("DB_PASSWORD")

password_escaped = urllib.parse.quote_plus(DB_PASSWORD)

# Si usas POOLER, el usuario DEBE ser postgres.PROJECT_REF
dsn = f"postgresql://postgres.{PROJECT_REF}:{password_escaped}@aws-0-ca-central-1.pooler.supabase.com:5432/postgres"

db = Database(dsn)


if not SUPABASE_DB_URL:
    raise ValueError("Falta configurar la variable de entorno SUPABASE_DB_URL")

# Sitio de Mercado Libre (MLA = Argentina)
SITE_ID = os.environ.get("SITE_ID", "MLA")

# Categorías a rastrear, separadas por coma (ej: "MLA1276,MLA1051")
CATEGORY_IDS = [c.strip() for c in os.environ.get("CATEGORY_IDS", "").split(",") if c.strip()]

# Tope de publicaciones a traer por categoría en cada corrida
MAX_ITEMS_PER_CATEGORY = int(os.environ.get("MAX_ITEMS_PER_CATEGORY", "200"))
