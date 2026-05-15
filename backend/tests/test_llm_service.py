from datetime import date

import httpx

from app.schemas.trip import TripPlanRequest
from app.services.llm_service import LLMClient, LLMSettings, build_assistant_reply, generate_trip_with_llm


class FakeTransport:
    def __init__(self, payload: dict):
        self.payload = payload
        self.requests = []

    def post(self, url: str, **kwargs):
        self.requests.append((url, kwargs))
        return FakeResponse(self.payload)


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FailingTransport:
    def post(self, url: str, **kwargs):
        raise RuntimeError("provider rejected request")


class TimeoutTransport:
    def post(self, url: str, **kwargs):
        raise httpx.ReadTimeout("provider timeout")


def test_llm_client_returns_chat_completion_content():
    transport = FakeTransport({"choices": [{"message": {"content": "真实模型回复"}}]})
    client = LLMClient(
        LLMSettings(
            api_key="test-key",
            model="test-model",
            base_url="https://llm.example/v1",
            timeout_seconds=3,
        ),
        transport=transport,
    )

    content = client.create_chat_completion([{"role": "user", "content": "你好"}])

    assert content == "真实模型回复"
    assert transport.requests[0][0] == "https://llm.example/v1/chat/completions"
    assert transport.requests[0][1]["headers"]["Authorization"] == "Bearer test-key"
    assert transport.requests[0][1]["json"]["model"] == "test-model"


def test_llm_client_is_disabled_without_api_key():
    client = LLMClient(LLMSettings(api_key="", model="test-model"))

    assert not client.is_enabled


def test_chat_fallback_explains_provider_failure_when_key_is_configured():
    client = LLMClient(
        LLMSettings(api_key="test-key", model="bad-model"),
        transport=FailingTransport(),
    )

    content = build_assistant_reply("帮我规划杭州两日游", client)

    assert "大模型调用失败" in content
    assert "bad-model" in content


def test_chat_fallback_explains_timeout_is_provider_response_problem():
    client = LLMClient(
        LLMSettings(
            api_key="test-key",
            model="slow-model",
            base_url="https://api.siliconflow.cn/v1",
            timeout_seconds=12,
        ),
        transport=TimeoutTransport(),
    )

    content = build_assistant_reply("从湘潭到萍乡", client)

    assert "模型服务响应超时" in content
    assert "后端已经启动" in content
    assert "12 秒" in content


def test_chat_prompt_requires_readable_sections_instead_of_wall_of_text():
    transport = FakeTransport({"choices": [{"message": {"content": "分段回复"}}]})
    client = LLMClient(LLMSettings(api_key="test-key", model="test-model"), transport=transport)

    build_assistant_reply("我想从长沙到西安旅行三天", client)

    system_prompt = transport.requests[0][1]["json"]["messages"][0]["content"]
    assert "不要输出一整段长文本" in system_prompt
    assert "使用清晰小标题" in system_prompt
    assert "每段不超过" in system_prompt


def test_generate_trip_with_llm_parses_structured_itinerary():
    payload = TripPlanRequest(
        origin="上海",
        destination="杭州",
        start_date=date(2026, 6, 1),
        days=1,
        budget="3000",
        preferences=["美食"],
    )
    client = LLMClient(
        LLMSettings(api_key="test-key", model="test-model"),
        transport=FakeTransport(
            {
                "choices": [
                    {
                        "message": {
                            "content": """
                            {
                              "summary": "杭州一日美食慢旅行",
                              "origin": "上海",
                              "destination": "杭州",
                              "weather": [],
                              "route_tips": ["高铁到达后优先使用地铁。"],
                              "days": [
                                {
                                  "day": 1,
                                  "theme": "西湖与美食",
                                  "schedule": [
                                    {
                                      "time": "09:30",
                                      "title": "西湖散步",
                                      "description": "从湖滨开始慢慢游览。"
                                    }
                                  ]
                                }
                              ],
                              "tips": ["提前预约热门餐厅。"]
                            }
                            """,
                        }
                    }
                ]
            }
        ),
    )

    result = generate_trip_with_llm(payload, client)

    assert result.summary == "杭州一日美食慢旅行"
    assert result.agent_trace == ["tool_context", "llm_planner"]
    assert result.days[0].schedule[0].title == "西湖散步"


def test_generate_trip_prompt_includes_tool_context_and_quality_rules():
    payload = TripPlanRequest(
        origin="上海",
        destination="西安",
        start_date=date(2026, 6, 1),
        days=3,
        budget="3000",
        preferences=["历史", "美食"],
    )
    transport = FakeTransport(
        {
            "choices": [
                {
                    "message": {
                        "content": """
                        {
                          "summary": "西安三日历史美食行程",
                          "origin": "上海",
                          "destination": "西安",
                          "weather": [],
                          "route_tips": ["优先地铁，跨区景点提前出发。"],
                          "days": [
                            {"day": 1, "theme": "城墙与钟鼓楼", "schedule": [{"time": "09:30", "title": "抵达西安", "description": "入住钟楼附近，方便步行。"}]},
                            {"day": 2, "theme": "兵马俑与华清宫", "schedule": [{"time": "08:30", "title": "前往临潼", "description": "乘地铁转公交，预留排队时间。"}]},
                            {"day": 3, "theme": "陕历博与大雁塔", "schedule": [{"time": "09:00", "title": "陕西历史博物馆", "description": "提前预约，重点看唐代展品。"}]}
                          ],
                          "tips": ["热门博物馆提前预约。"]
                        }
                        """,
                    }
                }
            ]
        }
    )
    client = LLMClient(LLMSettings(api_key="test-key", model="test-model"), transport=transport)

    generate_trip_with_llm(
        payload,
        client,
        tool_context={
            "places": ["秦始皇帝陵博物院", "陕西历史博物馆"],
            "weather": ["2026-06-01 晴 20-30 摄氏度"],
            "routes": ["上海到西安优先高铁或飞机，市内优先地铁。"],
        },
    )

    request_body = transport.requests[0][1]["json"]
    system_prompt = request_body["messages"][0]["content"]
    user_prompt = request_body["messages"][1]["content"]
    assert "秦始皇帝陵博物院" in user_prompt
    assert "陕西历史博物馆" in user_prompt
    assert "市内优先地铁" in user_prompt
    assert "不要返回空泛描述" in system_prompt
    assert "每一天至少 4 个时间段" in system_prompt
