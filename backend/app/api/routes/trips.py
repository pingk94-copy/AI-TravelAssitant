from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.trip import TripPlanRequest, TripResponse
from app.services.trip_service import get_user_trip, list_user_trips, plan_trip, to_trip_response

router = APIRouter(prefix="/trips", tags=["trips"])


@router.post("/plan", response_model=TripResponse, status_code=201)
def create_trip_plan(
    payload: TripPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TripResponse:
    trip = plan_trip(db, current_user, payload)
    return to_trip_response(trip)


@router.get("", response_model=list[TripResponse])
def read_trips(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TripResponse]:
    return [to_trip_response(trip) for trip in list_user_trips(db, current_user)]


@router.get("/{trip_id}", response_model=TripResponse)
def read_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TripResponse:
    return to_trip_response(get_user_trip(db, current_user, trip_id))
