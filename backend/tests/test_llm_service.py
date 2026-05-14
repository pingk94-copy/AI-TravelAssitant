from datetime import date

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


def test_llm_client_returns_chat_completion_content():
    transport = FakeTransport(
        {
            "choices": [
                {
                    "message": {
                        "content": "真实模型回复",
                    }
                }
            ]
        }
    )
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
    assert result.agent_trace == ["llm_planner"]
    assert result.days[0].schedule[0].title == "西湖散步"
