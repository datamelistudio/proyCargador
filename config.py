import os
import urllib.parse
from db import Database

# 1. Obtener variables de entorno
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
PROJECT_REF = os.getenv("PROJECT_REF")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# 2. Lógica para definir la cadena DSN
if SUPABASE_DB_URL:
    # Si definiste la URL completa en las variables de entorno, se usa directamente
    dsn = SUPABASE_DB_URL
elif PROJECT_REF and DB_PASSWORD:
    # Si tienes por separado el ID y la contraseña, se procesa de forma segura
    password_escaped = urllib.parse.quote_plus(str(DB_PASSWORD))
    
    # OPCIÓN A: Conexión Directa (Recomendada si corre 1 vez al día)
    dsn = f"postgresql://postgres:{password_escaped}@db.{PROJECT_REF}.supabase.co:5432/postgres"
    
    # OPCIÓN B: Si necesitas usar el Pooler (IPv4), descomenta la línea de abajo y comenta la Opción A:
    # dsn = f"postgresql://postgres.{PROJECT_REF}:{password_escaped}@aws-0-ca-central-1.pooler.supabase.com:5432/postgres"
else:
    raise ValueError(
        "Falta configurar las variables de entorno. Debes definir 'SUPABASE_DB_URL' "
        "o bien ambas variables 'PROJECT_REF' y 'DB_PASSWORD'."
    )

# 3. Inicializar la conexión una vez validado el DSN
db = Database(dsn)

# 4. Parámetros de la aplicación
SITE_ID = os.environ.get("SITE_ID", "MLA")

# Categorías a rastrear, separadas por coma (ej: "MLA1276,MLA1051")
CATEGORY_IDS = [c.strip() for c in os.environ.get("CATEGORY_IDS", "").split(",") if c.strip()]

# Tope de publicaciones a traer por categoría en cada corrida
MAX_ITEMS_PER_CATEGORY = int(os.environ.get("MAX_ITEMS_PER_CATEGORY", "200"))
