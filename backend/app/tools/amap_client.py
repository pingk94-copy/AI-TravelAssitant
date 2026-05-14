from typing import Any

import httpx

from app.core.config import settings


class AmapClient:
    def __init__(self, api_key: str = settings.amap_api_key, base_url: str = settings.amap_base_url) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def search_places(self, keyword: str, city: str | None = None) -> dict[str, Any] | None:
        if not self.is_configured:
            return None
        return self._get(
            "/place/text",
            {
                "keywords": keyword,
                "city": city or "",
                "offset": "5",
                "page": "1",
                "extensions": "base",
            },
        )

    def get_weather(self, city: str) -> dict[str, Any] | None:
        if not self.is_configured:
            return None
        return self._get("/weather/weatherInfo", {"city": city, "extensions": "all"})

    def plan_route(self, origin: str, destination: str, mode: str) -> dict[str, Any] | None:
        if not self.is_configured:
            return None

        endpoint = "/direction/walking" if mode == "walking" else "/direction/driving"
        return self._get(endpoint, {"origin": origin, "destination": destination})

    def _get(self, path: str, params: dict[str, str]) -> dict[str, Any] | None:
        try:
            with httpx.Client(timeout=settings.external_api_timeout_seconds) as client:
                response = client.get(f"{self.base_url}{path}", params={**params, "key": self.api_key})
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, ValueError):
            return None

        if data.get("status") != "1":
            return None
        return data
