from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.task import TaskSubmitResponse
from app.schemas.trip import TripPlanRequest, TripResponse
from app.services.trip_service import delete_trip, get_user_trip, list_user_trips, plan_trip, to_trip_response
from app.services.task_service import complete_task, create_task, fail_task

router = APIRouter(prefix="/trips", tags=["trips"])


@router.post("/plan", response_model=TripResponse, status_code=201)
def create_trip_plan(
    payload: TripPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TripResponse:
    trip = plan_trip(db, current_user, payload)
    return to_trip_response(trip)


@router.post("/plan-async", response_model=TaskSubmitResponse, status_code=202)
def create_trip_plan_task(
    payload: TripPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskSubmitResponse:
    task = create_task(db, current_user, "trip_plan", payload.model_dump(mode="json"))
    try:
        trip = plan_trip(db, current_user, payload)
        task = complete_task(db, task, {"trip": to_trip_response(trip).model_dump(mode="json")})
    except Exception as exc:
        task = fail_task(db, task, str(exc))

    return TaskSubmitResponse(task_id=task.id, status=task.status)


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


@router.delete("/{trip_id}", status_code=204)
def delete_trip_plan(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    trip = get_user_trip(db, current_user, trip_id)
    delete_trip(db, trip)
