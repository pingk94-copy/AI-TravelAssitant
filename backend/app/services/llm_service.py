from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import httpx
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.trip import ItineraryResult, TripPlanRequest


@dataclass(frozen=True)
class LLMSettings:
    api_key: str
    model: str
    base_url: str = "https://api.openai.com/v1"
    timeout_seconds: float = 30.0


class LLMClient:
    def __init__(self, llm_settings: LLMSettings | None = None, transport: Any | None = None) -> None:
        self.settings = llm_settings or LLMSettings(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            base_url=settings.openai_base_url,
            timeout_seconds=settings.openai_timeout_seconds,
        )
        self.transport = transport or httpx.Client(timeout=self.settings.timeout_seconds)

    @property
    def is_enabled(self) -> bool:
        return bool(self.settings.api_key.strip())

    def create_chat_completion(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.7,
        response_format: dict[str, str] | None = None,
    ) -> str:
        if not self.is_enabled:
            raise RuntimeError("OpenAI API key is not configured.")

        body: dict[str, Any] = {
            "model": self.settings.model,
            "messages": messages,
            "temperature": temperature,
        }
        if response_format is not None:
            body["response_format"] = response_format

        response = self.transport.post(
            f"{self.settings.base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.settings.api_key}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=self.settings.timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        return str(data["choices"][0]["message"]["content"])


def default_llm_client() -> LLMClient:
    return LLMClient()


def build_fallback_assistant_reply(user_message: str) -> str:
    return (
        "我已经收到你的旅行需求："
        f"{user_message}。"
        "当前还没有配置 OPENAI_API_KEY，所以先使用本地演示回复。"
        "填好后端 .env 里的密钥并重启服务后，这里会切换为真实大模型生成。"
    )


def build_llm_error_reply(user_message: str, client: LLMClient, error: Exception) -> str:
    return (
        "我已经收到你的旅行需求："
        f"{user_message}。"
        "但这次大模型调用失败了，请检查后端 .env 里的 "
        "OPENAI_BASE_URL、OPENAI_MODEL 和 OPENAI_API_KEY 是否属于同一个服务商。"
        f"当前模型：{client.settings.model}；当前接口：{client.settings.base_url}。"
        f"错误类型：{error.__class__.__name__}。"
    )


def build_assistant_reply(user_message: str, client: LLMClient | None = None) -> str:
    llm = client or default_llm_client()
    if not llm.is_enabled:
        return build_fallback_assistant_reply(user_message)

    messages = [
        {
            "role": "system",
            "content": (
                "你是一个中文旅行规划助手。回答要自然、具体、可执行。"
                "优先给出路线、节奏、餐饮、交通和注意事项。"
            ),
        },
        {"role": "user", "content": user_message},
    ]
    try:
        return llm.create_chat_completion(messages)
    except Exception as exc:
        return build_llm_error_reply(user_message, llm, exc)


def stream_sse_tokens(text: str) -> Iterable[str]:
    for token in text.split(" "):
        yield f"event: token\ndata: {token} \n\n"
    yield "event: done\ndata: [DONE]\n\n"


def generate_trip_with_llm(payload: TripPlanRequest, client: LLMClient | None = None) -> ItineraryResult | None:
    llm = client or default_llm_client()
    if not llm.is_enabled:
        return None

    prompt = _trip_prompt(payload)
    try:
        content = llm.create_chat_completion(
            [
                {
                    "role": "system",
                    "content": (
                        "你是专业中文旅行规划师。只返回 JSON，不要 Markdown。"
                        "JSON 必须符合用户给定字段，days 数量必须等于用户的游玩天数。"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            response_format={"type": "json_object"},
        )
        data = _parse_json_object(content)
        data["origin"] = data.get("origin") or payload.origin
        data["destination"] = data.get("destination") or payload.destination
        data.setdefault("weather", [])
        data.setdefault("route_tips", [])
        data.setdefault("tips", [])
        data["agent_trace"] = ["llm_planner"]
        return ItineraryResult.model_validate(data)
    except (ValueError, KeyError, ValidationError, httpx.HTTPError, RuntimeError):
        return None


def _trip_prompt(payload: TripPlanRequest) -> str:
    preferences = "、".join(payload.preferences) if payload.preferences else "均衡体验"
    return f"""
请生成一份中文旅行行程 JSON。

输入：
- 出发地：{payload.origin}
- 目的地：{payload.destination}
- 出发日期：{payload.start_date.isoformat()}
- 游玩天数：{payload.days}
- 预算：{payload.budget or "未填写"}
- 偏好：{preferences}

只返回这个结构：
{{
  "summary": "一段总体说明",
  "origin": "{payload.origin}",
  "destination": "{payload.destination}",
  "weather": [],
  "route_tips": ["路线建议 1"],
  "days": [
    {{
      "day": 1,
      "theme": "当天主题",
      "schedule": [
        {{"time": "09:30", "title": "安排标题", "description": "具体说明"}}
      ]
    }}
  ],
  "tips": ["出行提醒 1"]
}}
""".strip()


def _parse_json_object(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    return json.loads(text)
