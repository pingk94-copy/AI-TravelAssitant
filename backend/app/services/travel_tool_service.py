from app.schemas.tools import (
    PlaceItem,
    PlaceSearchResponse,
    RouteResponse,
    RouteStep,
    WeatherForecastItem,
    WeatherResponse,
)
from app.tools.amap_client import AmapClient


def search_places(keyword: str, city: str | None = None, client: AmapClient | None = None) -> PlaceSearchResponse:
    amap = client or AmapClient()
    data = amap.search_places(keyword, city)

    if data:
        pois = data.get("pois", [])[:5]
        items = [
            PlaceItem(
                name=poi.get("name") or keyword,
                address=_string_or_joined(poi.get("address")) or city or "Address unavailable",
                location=poi.get("location"),
            )
            for poi in pois
        ]
        if items:
            return PlaceSearchResponse(source="amap", keyword=keyword, city=city, items=items)

    return PlaceSearchResponse(
        source="fallback",
        keyword=keyword,
        city=city,
        items=[
            PlaceItem(
                name=keyword,
                address=f"{city or 'Selected city'} travel area",
                location=None,
            )
        ],
    )


def get_weather(city: str, client: AmapClient | None = None) -> WeatherResponse:
    amap = client or AmapClient()
    data = amap.get_weather(city)

    if data:
        forecasts = data.get("forecasts", [])
        casts = forecasts[0].get("casts", []) if forecasts else []
        items = [
            WeatherForecastItem(
                date=cast.get("date") or "Unknown date",
                weather=cast.get("dayweather") or cast.get("nightweather") or "Unknown",
                temperature=_temperature_range(cast.get("nighttemp"), cast.get("daytemp")),
                wind=cast.get("daywind"),
            )
            for cast in casts[:4]
        ]
        if items:
            return WeatherResponse(source="amap", city=city, forecast=items)

    return WeatherResponse(
        source="fallback",
        city=city,
        forecast=[
            WeatherForecastItem(
                date="Planning day",
                weather="Weather data unavailable",
                temperature="Check before departure",
                wind=None,
            )
        ],
    )


def plan_route(origin: str, destination: str, city: str | None, mode: str, client: AmapClient | None = None) -> RouteResponse:
    amap = client or AmapClient()
    data = amap.plan_route(origin, destination, mode)

    if data:
        route = data.get("route", {})
        paths = route.get("paths", [])
        steps_data = paths[0].get("steps", []) if paths else []
        steps = [
            RouteStep(
                instruction=step.get("instruction") or f"Move toward {destination}",
                distance=step.get("distance"),
                duration=step.get("duration"),
            )
            for step in steps_data[:8]
        ]
        if steps:
            return RouteResponse(source="amap", origin=origin, destination=destination, mode=mode, steps=steps)

    return RouteResponse(
        source="fallback",
        origin=origin,
        destination=destination,
        mode=mode,
        steps=[
            RouteStep(
                instruction=f"Use local map navigation from {origin} to {destination} in {city or 'the destination city'}.",
                distance=None,
                duration=None,
            )
        ],
    )


def _string_or_joined(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return ", ".join(str(item) for item in value if item)
    return ""


def _temperature_range(low: object, high: object) -> str:
    low_text = str(low) if low not in (None, "") else "?"
    high_text = str(high) if high not in (None, "") else "?"
    return f"{low_text}-{high_text} C"
