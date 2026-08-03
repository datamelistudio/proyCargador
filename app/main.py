import logging
import sys
from datetime import date

import config
from db import Database
from ml_client import MercadoLibreClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("carga_diaria")


def chunk(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def main():
    log.info("Inicio de carga diaria - %s", date.today().isoformat())

    if not config.CATEGORY_IDS:
        log.error("No hay categorías configuradas en la variable CATEGORY_IDS. Abortando.")
        sys.exit(1)

    db = Database(config.SUPABASE_DB_URL)
    ml = MercadoLibreClient(site_id=config.SITE_ID)

    seller_cache = {}
    total_items = 0

    try:
        for category_id in config.CATEGORY_IDS:
            log.info("Procesando categoría %s", category_id)

            categoria = ml.get_category(category_id)
            if categoria:
                db.upsert_categoria(category_id, categoria.get("name"))

            item_ids = ml.search_item_ids(category_id, max_items=config.MAX_ITEMS_PER_CATEGORY)
            log.info("  %d publicaciones encontradas", len(item_ids))

            for lote in chunk(item_ids, 20):
                items = ml.get_items(lote)
                for item in items:
                    if item is None:
                        continue

                    seller_id = str(item.get("seller_id"))
                    if seller_id not in seller_cache:
                        seller_cache[seller_id] = ml.get_seller(seller_id)
                    seller = seller_cache[seller_id] or {}

                    db.upsert_vendedor(
                        seller_id,
                        nickname=seller.get("nickname"),
                        reputacion=(seller.get("seller_reputation") or {}).get("level_id"),
                    )

                    db.upsert_producto(
                        item_id=item["id"],
                        category_id=item.get("category_id", category_id),
                        seller_id=seller_id,
                        titulo=item.get("title"),
                        condicion=item.get("condition"),
                    )

                    db.insert_captura(
                        item_id=item["id"],
                        precio=item.get("price"),
                        sold_quantity=item.get("sold_quantity", 0),
                        available_quantity=item.get("available_quantity", 0),
                        es_full=(item.get("shipping") or {}).get("logistic_type") == "fulfillment",
                        fecha_captura=date.today(),
                    )

                    total_items += 1
    finally:
        db.close()

    log.info("Carga diaria finalizada. %d publicaciones procesadas.", total_items)


if __name__ == "__main__":
    main()
