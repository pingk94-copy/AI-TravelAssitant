from app.schemas.tools import PlaceSearchResponse, RouteResponse, WeatherResponse
from app.schemas.trip import TripPlanRequest
from app.services.travel_tool_service import get_weather, plan_route, search_places


class WeatherSearchAgent:
    name = "weather_search_agent"

    def run(self, payload: TripPlanRequest) -> WeatherResponse:
        return get_weather(payload.destination)


class POISearchAgent:
    name = "poi_search_agent"

    def run(self, payload: TripPlanRequest) -> PlaceSearchResponse:
        keywords = " ".join(payload.preferences) if payload.preferences else "scenic food culture"
        return search_places(keywords, payload.destination)


class RouteSearchAgent:
    name = "route_search_agent"

    def run(self, payload: TripPlanRequest) -> RouteResponse:
        return plan_route(payload.origin, payload.destination, payload.destination, "walking")
