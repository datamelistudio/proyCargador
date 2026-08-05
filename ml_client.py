import logging
import time

import requests

log = logging.getLogger("carga_diaria")

BASE_URL = "https://api.mercadolibre.com"


class MercadoLibreClient:
    """Wrapper liviano sobre la API pública de Mercado Libre (sin OAuth,
    suficiente para los endpoints de categorías, destacados, items y usuarios).

    NOTA: el endpoint /sites/{site}/search fue restringido por Mercado Libre
    (devuelve 403 para la mayoría de las apps, con o sin token). En su lugar
    usamos /highlights/{site}/category/{category_id}, que sigue disponible
    públicamente y devuelve las publicaciones/productos destacados de una
    categoría.
    """

    def __init__(self, site_id="MLA", timeout=15, max_retries=3):
        self.site_id = site_id
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()

    def _get(self, path, params=None):
        url = f"{BASE_URL}{path}"
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout)
                if resp.status_code == 200:
                    return resp.json()
                log.warning("GET %s -> status %s (intento %d/%d)", url, resp.status_code, attempt, self.max_retries)
            except requests.RequestException as e:
                log.warning("Error en GET %s: %s (intento %d/%d)", url, e, attempt, self.max_retries)
            time.sleep(1.5 * attempt)
        return None

    def get_category(self, category_id):
        return self._get(f"/categories/{category_id}")

    def discover_category(self, texto_busqueda):
        """Dado un texto libre (ej: 'cajas de carton'), devuelve las
        categorías/dominios sugeridos por ML, con su category_id."""
        return self._get(
            f"/sites/{self.site_id}/domain_discovery/search",
            params={"q": texto_busqueda},
        )

    def _resolve_product_to_item(self, product_id):
        """Un 'product_id' es un ID de catálogo (no de publicación). Lo resolvemos
        al item que gana el buy-box, que es el que se puede usar en /items."""
        data = self._get(f"/products/{product_id}")
        if not data:
            return None
        return data.get("buy_box_winner_item_id")

    def search_item_ids(self, category_id, max_items=200, page_size=50):
        """Obtiene item_ids destacados de una categoría usando /highlights,
        en reemplazo de /sites/{site}/search (bloqueado por ML)."""
        item_ids = []

        data = self._get(f"/highlights/{self.site_id}/category/{category_id}")
        if not data or not data.get("content"):
            log.warning("Sin resultados de highlights para categoría %s", category_id)
            return item_ids

        for entry in data["content"]:
            if len(item_ids) >= max_items:
                break

            entry_id = entry.get("id")
            entry_type = entry.get("type")
            if not entry_id:
                continue

            if entry_type == "ITEM":
                item_ids.append(entry_id)
            elif entry_type == "PRODUCT":
                resolved_item_id = self._resolve_product_to_item(entry_id)
                if resolved_item_id:
                    item_ids.append(resolved_item_id)
            else:
                log.warning("Tipo de highlight desconocido (%s) para id %s", entry_type, entry_id)

        return item_ids[:max_items]

    def get_items(self, item_ids):
        """Trae el detalle de hasta 20 items en una sola llamada (multiget)."""
        data = self._get("/items", params={"ids": ",".join(item_ids)})
        if not data:
            return []
        resultados = []
        for entry in data:
            if entry.get("code") == 200 and "body" in entry:
                resultados.append(entry["body"])
            else:
                resultados.append(None)
        return resultados

    def get_seller(self, seller_id):
        return self._get(f"/users/{seller_id}")
