from app.agents.search_agents import POISearchAgent, RouteSearchAgent, WeatherSearchAgent
from app.schemas.trip import ItineraryResult, ItineraryScheduleItem, TripPlanRequest


class PlannerAgent:
    name = "planner_agent"

    def __init__(
        self,
        weather_agent: WeatherSearchAgent | None = None,
        poi_agent: POISearchAgent | None = None,
        route_agent: RouteSearchAgent | None = None,
    ) -> None:
        self.weather_agent = weather_agent or WeatherSearchAgent()
        self.poi_agent = poi_agent or POISearchAgent()
        self.route_agent = route_agent or RouteSearchAgent()

    def plan(self, payload: TripPlanRequest) -> ItineraryResult:
        weather = self.weather_agent.run(payload)
        places = self.poi_agent.run(payload)
        route = self.route_agent.run(payload)
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
                "This itinerary was coordinated by Planner Agent with weather, POI, and route search agents.",
            ],
            agent_trace=[
                self.weather_agent.name,
                self.poi_agent.name,
                self.route_agent.name,
                self.name,
            ],
        )
