import logging
import time

import requests

log = logging.getLogger("carga_diaria")

BASE_URL = "https://api.mercadolibre.com"


class MercadoLibreClient:
    """Wrapper liviano sobre la API pública de Mercado Libre (sin OAuth,
    suficiente para los endpoints de categorías, búsqueda, items y usuarios)."""

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

    def search_item_ids(self, category_id, max_items=200, page_size=50):
        """Pagina el buscador público y devuelve una lista de item_ids."""
        item_ids = []
        offset = 0
        while offset < max_items:
            data = self._get(
                f"/sites/{self.site_id}/search",
                params={"category": category_id, "limit": page_size, "offset": offset},
            )
            if not data or not data.get("results"):
                break
            item_ids.extend([r["id"] for r in data["results"]])
            offset += page_size
            total_disponible = data.get("paging", {}).get("total", 0)
            if offset >= total_disponible:
                break
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
