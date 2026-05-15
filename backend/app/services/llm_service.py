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
        key = self.settings.api_key.strip()
        return bool(key) and key != "your_api_key_here"

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
        "### 当前状态\n"
        "后端还没有配置有效的 `OPENAI_API_KEY`，所以这条回复来自本地兜底逻辑。\n\n"
        "### 我收到的需求\n"
        f"{user_message}\n\n"
        "### 下一步\n"
        "请在 `backend/.env` 填入真实密钥并重启项目，聊天和行程规划就会优先调用大模型。"
    )


def build_llm_error_reply(user_message: str, client: LLMClient, error: Exception) -> str:
    if isinstance(error, httpx.ReadTimeout):
        return (
            "### 模型服务响应超时\n"
            "后端已经启动，也已经收到你的请求，但外部模型服务没有在限定时间内返回。\n\n"
            "### 当前连接\n"
            f"- 当前模型：`{client.settings.model}`\n"
            f"- 当前接口：`{client.settings.base_url}`\n"
            f"- 超时时间：{client.settings.timeout_seconds:g} 秒\n\n"
            "### 可以怎么处理\n"
            "- 先确认 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL` 属于同一个服务商\n"
            "- 如果配置正确，通常是服务商网络或模型排队，请稍后重试\n"
            "- 也可以把 `OPENAI_TIMEOUT_SECONDS` 调大后重启项目\n\n"
            "### 本次请求\n"
            f"{user_message}\n\n"
            "错误类型：`ReadTimeout`"
        )

    return (
        "### 大模型调用失败\n"
        "后端已经收到你的请求，但模型服务没有成功返回。\n\n"
        "### 请检查\n"
        f"- 当前模型：`{client.settings.model}`\n"
        f"- 当前接口：`{client.settings.base_url}`\n"
        "- `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL` 是否属于同一个服务商\n\n"
        "### 本次请求\n"
        f"{user_message}\n\n"
        f"错误类型：`{error.__class__.__name__}`"
    )


def build_assistant_reply(user_message: str, client: LLMClient | None = None) -> str:
    llm = client or default_llm_client()
    if not llm.is_enabled:
        return build_fallback_assistant_reply(user_message)

    messages = [
        {
            "role": "system",
            "content": (
                "你是一个中文旅行规划助手。回答必须具体、可执行、适合直接阅读。"
                "不要输出一整段长文本；使用清晰小标题、短段落和项目符号。"
                "每段不超过 80 个中文字符。"
                "涉及行程时必须包含交通、住宿区域、时间安排、餐饮建议、预约提醒和预算注意。"
                "不要用空话，例如“根据个人情况调整”必须改成具体可执行建议。"
            ),
        },
        {"role": "user", "content": user_message},
    ]
    try:
        return llm.create_chat_completion(messages, temperature=0.5)
    except Exception as exc:
        return build_llm_error_reply(user_message, llm, exc)


def stream_sse_tokens(text: str) -> Iterable[str]:
    chunk = []
    for char in text:
        chunk.append(char)
        if char in "\n。！？；" or len(chunk) >= 24:
            yield f"event: token\ndata: {''.join(chunk)}\n\n"
            chunk = []
    if chunk:
        yield f"event: token\ndata: {''.join(chunk)}\n\n"
    yield "event: done\ndata: [DONE]\n\n"


def generate_trip_with_llm(
    payload: TripPlanRequest,
    client: LLMClient | None = None,
    tool_context: dict[str, list[str]] | None = None,
) -> ItineraryResult | None:
    llm = client or default_llm_client()
    if not llm.is_enabled:
        return None

    try:
        content = llm.create_chat_completion(
            [
                {
                    "role": "system",
                    "content": (
                        "你是专业中文旅行规划师。只返回 JSON，不要 Markdown。"
                        "JSON 必须符合用户给定字段，days 数量必须等于游玩天数。"
                        "不要返回空泛描述，不要重复同一句话。"
                        "每一天至少 4 个时间段，必须覆盖上午、午餐、下午、晚间。"
                        "每个 schedule.description 必须包含具体地点、交通方式或预约/排队/预算提醒。"
                        "route_tips 至少 2 条，tips 至少 3 条。"
                    ),
                },
                {"role": "user", "content": _trip_prompt(payload, tool_context or {})},
            ],
            temperature=0.35,
            response_format={"type": "json_object"},
        )
        data = _parse_json_object(content)
        data["origin"] = data.get("origin") or payload.origin
        data["destination"] = data.get("destination") or payload.destination
        data.setdefault("weather", tool_context.get("weather", []) if tool_context else [])
        data.setdefault("route_tips", tool_context.get("routes", []) if tool_context else [])
        data.setdefault("tips", [])
        data["agent_trace"] = ["tool_context", "llm_planner"]
        return ItineraryResult.model_validate(data)
    except (ValueError, KeyError, ValidationError, httpx.HTTPError, RuntimeError, TypeError):
        return None


def _trip_prompt(payload: TripPlanRequest, tool_context: dict[str, list[str]]) -> str:
    preferences = "、".join(payload.preferences) if payload.preferences else "经典景点、在地美食、交通便利"
    places = "\n".join(f"- {item}" for item in tool_context.get("places", [])) or "- 暂无景点工具数据，请基于目的地常识规划"
    weather = "\n".join(f"- {item}" for item in tool_context.get("weather", [])) or "- 暂无天气工具数据，请提醒用户出发前复查"
    routes = "\n".join(f"- {item}" for item in tool_context.get("routes", [])) or "- 暂无路线工具数据，请给出跨城与市内交通建议"
    return f"""
请生成一份中文旅行行程 JSON。

用户输入：
- 出发地：{payload.origin}
- 目的地：{payload.destination}
- 出发日期：{payload.start_date.isoformat()}
- 游玩天数：{payload.days}
- 预算：{payload.budget or "未填写"}
- 偏好：{preferences}

可用工具上下文：
景点/POI：
{places}

天气：
{weather}

路线：
{routes}

返回 JSON 结构：
{{
  "summary": "一句有信息量的总体说明，说明路线重点和节奏",
  "origin": "{payload.origin}",
  "destination": "{payload.destination}",
  "weather": [{{"date": "日期", "weather": "天气", "temperature": "温度", "wind": "风向"}}],
  "route_tips": ["具体路线建议"],
  "days": [
    {{
      "day": 1,
      "theme": "当天主题",
      "schedule": [
        {{"time": "09:00", "title": "具体安排", "description": "地点 + 交通/预约/预算/排队提醒"}}
      ]
    }}
  ],
  "tips": ["具体提醒"]
}}
""".strip()


def _parse_json_object(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    return json.loads(text)
