import psycopg2


class Database:
    def __init__(self, dsn):
        self.conn = psycopg2.connect(dsn)
        self.conn.autocommit = True

    def close(self):
        self.conn.close()

    def upsert_categoria(self, category_id, nombre):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO dim_categorias (category_id, nombre_categoria, updated_at)
                VALUES (%s, %s, now())
                ON CONFLICT (category_id)
                DO UPDATE SET nombre_categoria = EXCLUDED.nombre_categoria, updated_at = now()
                """,
                (category_id, nombre),
            )

    def upsert_vendedor(self, seller_id, nickname, reputacion):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO dim_vendedores (seller_id, nickname, reputacion_nivel)
                VALUES (%s, %s, %s)
                ON CONFLICT (seller_id)
                DO UPDATE SET nickname = EXCLUDED.nickname,
                              reputacion_nivel = EXCLUDED.reputacion_nivel
                """,
                (seller_id, nickname, reputacion),
            )

    def upsert_producto(self, item_id, category_id, seller_id, titulo, condicion):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO dim_productos (item_id, category_id, seller_id, titulo_publicacion, condicion)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (item_id)
                DO UPDATE SET category_id = EXCLUDED.category_id,
                              seller_id = EXCLUDED.seller_id,
                              titulo_publicacion = EXCLUDED.titulo_publicacion,
                              condicion = EXCLUDED.condicion
                """,
                (item_id, category_id, seller_id, titulo, condicion),
            )

    def insert_captura(self, item_id, precio, sold_quantity, available_quantity, es_full, fecha_captura):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO fact_historico_mercado
                    (item_id, precio, sold_quantity, available_quantity, es_full, fecha_captura)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (item_id, fecha_captura)
                DO UPDATE SET precio = EXCLUDED.precio,
                              sold_quantity = EXCLUDED.sold_quantity,
                              available_quantity = EXCLUDED.available_quantity,
                              es_full = EXCLUDED.es_full
                """,
                (item_id, precio, sold_quantity, available_quantity, es_full, fecha_captura),
            )
