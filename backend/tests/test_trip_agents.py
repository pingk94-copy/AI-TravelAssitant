from datetime import date

from app.agents.planner_agent import PlannerAgent
from app.schemas.trip import TripPlanRequest


def test_planner_agent_coordinates_three_search_agents():
    planner = PlannerAgent()
    payload = TripPlanRequest(
        origin="Shanghai",
        destination="Hangzhou",
        start_date=date(2026, 6, 1),
        days=2,
        budget="3000",
        preferences=["food", "relaxed", "scenic"],
    )

    result = planner.plan(payload)

    assert result.destination == "Hangzhou"
    assert len(result.days) == 2
    assert result.agent_trace == [
        "weather_search_agent",
        "poi_search_agent",
        "route_search_agent",
        "planner_agent",
    ]
    assert result.weather
    assert result.route_tips
    assert result.days[0].schedule[0].title
