from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.user import User
from app.schemas.tools import (
    PlaceSearchRequest,
    PlaceSearchResponse,
    RouteRequest,
    RouteResponse,
    WeatherRequest,
    WeatherResponse,
)
from app.services.travel_tool_service import get_weather, plan_route, search_places

router = APIRouter(prefix="/tools", tags=["tools"])


@router.post("/places/search", response_model=PlaceSearchResponse)
def search_place_tool(
    payload: PlaceSearchRequest,
    _: User = Depends(get_current_user),
) -> PlaceSearchResponse:
    return search_places(payload.keyword, payload.city)


@router.post("/weather", response_model=WeatherResponse)
def weather_tool(
    payload: WeatherRequest,
    _: User = Depends(get_current_user),
) -> WeatherResponse:
    return get_weather(payload.city)


@router.post("/routes", response_model=RouteResponse)
def route_tool(
    payload: RouteRequest,
    _: User = Depends(get_current_user),
) -> RouteResponse:
    return plan_route(payload.origin, payload.destination, payload.city, payload.mode)
