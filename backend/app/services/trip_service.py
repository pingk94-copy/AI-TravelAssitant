from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.planner_agent import PlannerAgent
from app.models.trip import Trip
from app.models.user import User
from app.schemas.trip import ItineraryResult, TripPlanRequest, TripResponse
from app.services.llm_service import generate_trip_with_llm


def plan_trip(db: Session, user: User, payload: TripPlanRequest) -> Trip:
    result = build_itinerary(payload)
    trip = Trip(
        user_id=user.id,
        title=f"{payload.destination} {payload.days} 天游",
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="行程不存在")
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
    llm_result = generate_trip_with_llm(payload)
    if llm_result is not None:
        return llm_result
    return PlannerAgent().plan(payload)
