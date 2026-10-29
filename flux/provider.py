"""Real OpenRouter adapter; no client construction or traffic during import/doctor."""

import asyncio
import json
from dataclasses import dataclass
from typing import Protocol

import httpx

from flux.config import Settings
from flux.errors import BudgetExceeded, ProviderError
from flux.memory import Store


class Model(Protocol):
    async def complete(
        self, messages: list[dict[str, str]], model: str, max_tokens: int, timeout: int
    ) -> str: ...


@dataclass
class Budget:
    store: Store
    max_calls: int
    daily_calls: int
    calls: int = 0

    def reserve(self) -> None:
        if self.calls >= self.max_calls:
            raise BudgetExceeded("turn_calls_exhausted")
        self.store.reserve_call(self.daily_calls)
        self.calls += 1


def classify(status: int) -> ProviderError:
    code = {
        400: "invalid_request",
        401: "authentication",
        402: "billing",
        403: "permission",
        404: "unsupported_model",
        408: "timeout",
        422: "invalid_request",
        429: "rate_limit",
    }.get(status, "unavailable" if 500 <= status <= 599 else "provider_rejected")
    return ProviderError(code, status in (408, 429) or 500 <= status <= 599)


class OpenRouter:
    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None):
        settings.validate("local")
        self.settings = settings
        self.transport = transport

    async def complete(
        self, messages: list[dict[str, str]], model: str, max_tokens: int, timeout: int
    ) -> str:
        try:
            async with httpx.AsyncClient(
                transport=self.transport, timeout=timeout, follow_redirects=False, trust_env=False
            ) as client:
                async with client.stream(
                    "POST",
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.settings.provider_key}"},
                    json={
                        "model": model,
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "stream": False,
                        "provider": {"allow_fallbacks": False},
                    },
                ) as response:
                    if response.status_code != 200:
                        raise classify(response.status_code)
                    payload = bytearray()
                    async for chunk in response.aiter_bytes():
                        payload.extend(chunk)
                        if len(payload) > 1000000:
                            raise ProviderError("invalid_output")
            data = json.loads(payload)
            if "error" in data:
                status = data["error"].get("code")
                raise (
                    classify(status) if type(status) is int else ProviderError("provider_rejected")
                )
            choice = data["choices"][0]
            if choice.get("finish_reason") not in ("stop", None):
                raise ProviderError("incomplete_output")
            content = choice["message"]["content"]
            if not isinstance(content, str) or not content.strip() or len(content) > 16000:
                raise ProviderError("invalid_output")
            return content.strip()
        except (httpx.TimeoutException, TimeoutError) as exc:
            raise ProviderError("timeout", True) from exc
        except httpx.HTTPError as exc:
            raise ProviderError("transport", True) from exc
        except (ValueError, KeyError, TypeError, IndexError, AttributeError) as exc:
            raise ProviderError("invalid_output") from exc


async def generate(
    model: Model,
    settings: Settings,
    budget: Budget,
    messages: list[dict[str, str]],
    summary: bool = False,
) -> str:
    primary = settings.summary_model if summary else settings.model
    candidates = [primary]
    if settings.fallback_enabled:
        candidates.extend(settings.fallback_models)
    for index, candidate in enumerate(candidates):
        budget.reserve()  # Count failures, timeouts, fallbacks and summaries before dispatch.
        try:
            async with asyncio.timeout(settings.timeout):
                result = await model.complete(
                    messages, candidate, settings.max_output_tokens, settings.timeout
                )
            if not isinstance(result, str) or not result.strip() or len(result) > 16000:
                raise ProviderError("invalid_output")
            return settings.redactor()(result)
        except TimeoutError as exc:
            error = ProviderError("timeout", True)
            if index == len(candidates) - 1:
                raise error from exc
        except ProviderError as exc:
            if not exc.retryable or index == len(candidates) - 1:
                raise
    raise ProviderError("unavailable")
