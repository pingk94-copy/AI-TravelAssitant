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
        preferences_text = "、".join(payload.preferences) if payload.preferences else "经典景点、在地美食、交通便利"
        place_names = [item.name for item in places.items] or [f"{payload.destination}核心游览区"]

        days = []
        for day_index in range(1, payload.days + 1):
            anchor = place_names[(day_index - 1) % len(place_names)]
            next_anchor = place_names[day_index % len(place_names)]
            days.append(
                {
                    "day": day_index,
                    "theme": f"{payload.destination}第 {day_index} 天：围绕{anchor}展开",
                    "schedule": [
                        ItineraryScheduleItem(
                            time="09:00",
                            title=f"抵达并前往{anchor}",
                            description=f"优先把住宿或集合点安排在交通方便的位置，上午前往{anchor}，减少跨城或跨区折返。",
                        ),
                        ItineraryScheduleItem(
                            time="11:30",
                            title="安排附近午餐",
                            description=f"在{anchor}周边寻找评分稳定、排队可控的本地餐馆，避免把午餐安排得离下一站太远。",
                        ),
                        ItineraryScheduleItem(
                            time="14:00",
                            title=f"串联{next_anchor}",
                            description=f"下午前往{next_anchor}或同一区域景点，按天气和体力选择深度参观或轻量散步。",
                        ),
                        ItineraryScheduleItem(
                            time="19:00",
                            title="晚餐与夜间调整",
                            description="晚餐后确认第二天交通、预约和天气；如果当天步行较多，第二天上午降低强度。",
                        ),
                    ],
                }
            )

        return ItineraryResult(
            summary=f"这是一份从{payload.origin}出发前往{payload.destination}的 {payload.days} 天游玩方案，围绕{preferences_text}安排，并尽量减少无意义折返。",
            origin=payload.origin,
            destination=payload.destination,
            weather=[item.model_dump() for item in weather.forecast],
            route_tips=[step.instruction for step in route.steps],
            days=days,
            tips=[
                f"预算参考：{payload.budget or '暂未填写'}。",
                "热门景点、博物馆、演出和餐厅请提前预约。",
                "本地兜底规划无法替代实时大模型；配置 OPENAI_API_KEY 后会优先调用大模型生成更细的行程。",
            ],
            agent_trace=[
                self.weather_agent.name,
                self.poi_agent.name,
                self.route_agent.name,
                self.name,
            ],
        )
