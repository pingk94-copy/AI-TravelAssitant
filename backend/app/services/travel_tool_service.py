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
        pois = data.get("pois", [])[:8]
        items = [
            PlaceItem(
                name=poi.get("name") or keyword,
                address=_string_or_joined(poi.get("address")) or city or "暂无地址信息",
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
                name=f"{city or '目的地'}核心游览区",
                address=f"{city or '目的地城市'}市中心或游客常去区域",
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
                date=cast.get("date") or "未知日期",
                weather=cast.get("dayweather") or cast.get("nightweather") or "未知天气",
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
                date="规划日",
                weather="暂无实时天气数据",
                temperature="出发前请再次确认",
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
                instruction=step.get("instruction") or f"前往{destination}",
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
                instruction=f"从{origin}前往{destination}建议优先查询高铁/航班；到达后市内优先使用地铁、公交或网约车。",
                distance=None,
                duration=None,
            ),
            RouteStep(
                instruction=f"在{city or destination}跨区游玩时，把相邻景点安排在同一天，减少往返。",
                distance=None,
                duration=None,
            ),
        ],
    )


def _string_or_joined(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return ", ".join(str(item) for item in value if item)
    return ""


def _temperature_range(low: object, high: object) -> str:
    low_text = str(low) if low not in (None, "") else "未知"
    high_text = str(high) if high not in (None, "") else "未知"
    return f"{low_text}-{high_text} 摄氏度"
