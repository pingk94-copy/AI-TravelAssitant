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
        preferences_text = "、".join(payload.preferences) if payload.preferences else "均衡节奏"
        place_names = [item.name for item in places.items] or [payload.destination]

        days = []
        for day_index in range(1, payload.days + 1):
            anchor = place_names[(day_index - 1) % len(place_names)]
            days.append(
                {
                    "day": day_index,
                    "theme": f"{payload.destination}第 {day_index} 天：{preferences_text}",
                    "schedule": [
                        ItineraryScheduleItem(
                            time="09:30",
                            title=f"从{anchor}开始",
                            description=f"以{anchor}作为当天核心锚点，安排一条适合在{payload.destination}慢慢游玩的路线。",
                        ),
                        ItineraryScheduleItem(
                            time="14:00",
                            title="周边弹性探索",
                            description="下午预留弹性时间，可根据体力和天气选择附近美食、观景点或室内备选地点。",
                        ),
                        ItineraryScheduleItem(
                            time="19:00",
                            title="晚间复盘与调整",
                            description="晚上确认交通时间，并根据当天体力和天气微调第二天安排。",
                        ),
                    ],
                }
            )

        return ItineraryResult(
            summary=f"这是一份从{payload.origin}出发前往{payload.destination}的 {payload.days} 天游玩方案，整体围绕{preferences_text}展开。",
            origin=payload.origin,
            destination=payload.destination,
            weather=[item.model_dump() for item in weather.forecast],
            route_tips=[step.instruction for step in route.steps],
            days=days,
            tips=[
                f"预算参考：{payload.budget or '暂未填写'}。",
                "出发前请再次确认实时天气和交通情况。",
                "本行程由 Planner Agent 协调天气、景点和路线搜索 Agent 共同生成。",
            ],
            agent_trace=[
                self.weather_agent.name,
                self.poi_agent.name,
                self.route_agent.name,
                self.name,
            ],
        )
