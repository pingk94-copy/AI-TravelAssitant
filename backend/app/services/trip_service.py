from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.trip import Trip
from app.models.user import User
from app.schemas.trip import ItineraryResult, ItineraryScheduleItem, TripPlanRequest, TripResponse
from app.services.travel_tool_service import get_weather, plan_route, search_places


def plan_trip(db: Session, user: User, payload: TripPlanRequest) -> Trip:
    result = build_itinerary(payload)
    trip = Trip(
        user_id=user.id,
        title=f"{payload.destination} {payload.days}-day trip",
        origin=payload.origin,
        destination=payload.destination,
        start_date=payload.start_date,
        days=payload.days,
        budget=payload.budget,
        preferences=payload.preferences,
        status="success",
        result_json=result.model_dump(),
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


def list_user_trips(db: Session, user: User) -> list[Trip]:
    return list(db.scalars(select(Trip).where(Trip.user_id == user.id).order_by(Trip.created_at.desc())))


def get_user_trip(db: Session, user: User, trip_id: int) -> Trip:
    trip = db.get(Trip, trip_id)
    if trip is None or trip.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return trip


def to_trip_response(trip: Trip) -> TripResponse:
    return TripResponse(
        id=trip.id,
        title=trip.title,
        origin=trip.origin,
        destination=trip.destination,
        start_date=trip.start_date,
        days=trip.days,
        budget=trip.budget,
        preferences=trip.preferences,
        status=trip.status,
        result=ItineraryResult.model_validate(trip.result_json),
        created_at=trip.created_at,
    )


def build_itinerary(payload: TripPlanRequest) -> ItineraryResult:
    weather = get_weather(payload.destination)
    places = search_places("scenic food culture", payload.destination)
    route = plan_route(payload.origin, payload.destination, payload.destination, "walking")
    preferences_text = ", ".join(payload.preferences) if payload.preferences else "balanced pace"
    place_names = [item.name for item in places.items] or [payload.destination]

    days = []
    for day_index in range(1, payload.days + 1):
        anchor = place_names[(day_index - 1) % len(place_names)]
        days.append(
            {
                "day": day_index,
                "theme": f"{payload.destination} day {day_index}: {preferences_text}",
                "schedule": [
                    ItineraryScheduleItem(
                        time="09:30",
                        title=f"Start with {anchor}",
                        description=f"Use {anchor} as the main anchor for a relaxed route in {payload.destination}.",
                    ),
                    ItineraryScheduleItem(
                        time="14:00",
                        title="Flexible local exploration",
                        description="Keep the afternoon open for nearby food, viewpoints, or weather-friendly indoor options.",
                    ),
                    ItineraryScheduleItem(
                        time="19:00",
                        title="Evening review",
                        description="Review transport time and adjust the next day based on energy and weather.",
                    ),
                ],
            }
        )

    return ItineraryResult(
        summary=f"A {payload.days}-day trip from {payload.origin} to {payload.destination} built around {preferences_text}.",
        origin=payload.origin,
        destination=payload.destination,
        weather=[item.model_dump() for item in weather.forecast],
        route_tips=[step.instruction for step in route.steps],
        days=days,
        tips=[
            f"Budget reference: {payload.budget or 'not specified'}.",
            "Check live weather and transport before departure.",
            "This MVP itinerary uses normalized tool outputs and can be upgraded to a Planner Agent later.",
        ],
    )
