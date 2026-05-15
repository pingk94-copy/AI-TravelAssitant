from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class TripPlanRequest(BaseModel):
    origin: str = Field(min_length=1, max_length=120)
    destination: str = Field(min_length=1, max_length=120)
    start_date: date
    days: int = Field(ge=1, le=5)
    budget: str | None = Field(default=None, max_length=80)
    preferences: list[str] = Field(default_factory=list, max_length=8)


class ItineraryScheduleItem(BaseModel):
    time: str
    title: str
    description: str


class ItineraryDay(BaseModel):
    day: int
    theme: str
    schedule: list[ItineraryScheduleItem]


class ItineraryResult(BaseModel):
    summary: str
    origin: str
    destination: str
    weather: list[dict[str, Any]]
    route_tips: list[str]
    days: list[ItineraryDay]
    tips: list[str]
    agent_trace: list[str] = Field(default_factory=list)


class TripResponse(BaseModel):
    id: int
    title: str
    origin: str
    destination: str
    start_date: date
    days: int
    budget: str | None
    preferences: list[str]
    status: str
    result: ItineraryResult
    created_at: datetime

    model_config = {"from_attributes": True}


class TripFavoriteResponse(BaseModel):
    id: int
    favorite_type: str
    target_id: int
    trip: TripResponse
    created_at: datetime
