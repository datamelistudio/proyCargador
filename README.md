# ml-market-intel-cron

Servicio de carga diaria: consulta la API pública de Mercado Libre y sube
precio/stock/ventas a las tablas de Supabase (`dim_categorias`,
`dim_vendedores`, `dim_productos`, `fact_historico_mercado`).

No requiere cuenta de vendedor ni OAuth: usa solo endpoints públicos
(`/sites/{site}/search`, `/items`, `/categories/{id}`, `/users/{id}`).

## Estructura

- `main.py` — orquesta la corrida completa.
- `ml_client.py` — llamadas a la API de Mercado Libre.
- `db.py` — upserts contra Postgres (Supabase) vía `psycopg2`.
- `config.py` — lee la configuración desde variables de entorno.

## Variables de entorno (Railway → Variables)

| Variable | Obligatoria | Descripción |
|---|---|---|
| `SUPABASE_DB_URL` | Sí | Connection string directa de Supabase (puerto 5432, no el pooler). Se obtiene en Supabase → Project Settings → Database → Connection string. |
| `SITE_ID` | No (default `MLA`) | Sitio de Mercado Libre. |
| `CATEGORY_IDS` | Sí | IDs de categoría a rastrear, separados por coma (ej: `MLA1276,MLA1051`). |
| `MAX_ITEMS_PER_CATEGORY` | No (default `200`) | Tope de publicaciones por categoría en cada corrida. |

## Despliegue en Railway

1. Subí esta carpeta a un repo de GitHub (o conectá el repo existente).
2. En Railway: **New Project → Deploy from GitHub repo**, elegí el repo.
3. Railway detecta `railway.toml` automáticamente:
   - `startCommand = "python main.py"`
   - `cronSchedule = "0 9 * * *"` (09:00 UTC = 06:00 Argentina — ajustalo a gusto en formato cron estándar).
   - `restartPolicyType = "NEVER"` — es obligatorio para servicios cron: cada corrida termina y no debe reiniciarse sola.
4. Cargá las variables de entorno de la tabla de arriba en **Variables**.
5. Hacé un deploy manual la primera vez para validar que corre bien antes de dejarlo en piloto automático con el cron.

## Notas

- El script hace upsert (no duplica filas): si se corre dos veces el mismo
  día, la fila de `fact_historico_mercado` para ese `item_id + fecha` se
  actualiza en vez de duplicarse (por el `UNIQUE(item_id, fecha_captura)`
  del schema).
- La detección de Full usa `shipping.logistic_type == "fulfillment"` del
  detalle del item.
- Los llamados a `/users/{seller_id}` se cachean en memoria durante la
  corrida para no repetir consultas del mismo vendedor.
- Si una categoría tiene muchas publicaciones y querés bajar más de 200
  por corrida, subí `MAX_ITEMS_PER_CATEGORY` (la API de búsqueda de ML
  limita el offset total a 1000 resultados por categoría).
