"""Defense in depth: do not log prompts, IDs, arguments, paths or exception bodies."""

import re
from collections.abc import Iterable


class Redactor:
    def __init__(self, secrets: Iterable[str] = ()):
        self.secrets = tuple(s for s in secrets if s)

    def __call__(self, text: str) -> str:
        for secret in sorted(self.secrets, key=len, reverse=True):
            text = text.replace(secret, "[REDACTED]")
        text = re.sub(r"sk-[A-Za-z0-9_-]{8,}", "[REDACTED]", text)
        text = re.sub(r"\b\d{5,}:[A-Za-z0-9_-]{20,}", "[REDACTED]", text)
        # Mask the whole quoted value, including whitespace and escaped quotes.
        # Preserve surrounding JSON/Python syntax so redaction cannot corrupt an answer.
        text = re.sub(
            r"""(["']?(?:api[_-]?key|token|password|secret)["']?\s*[:=]\s*)(["'])(?:\\.|(?!\2)[^\\])*\2""",
            lambda match: f"{match[1]}{match[2]}[REDACTED]{match[2]}",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        text = re.sub(
            r"(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*[^\s,;]+", r"\1=[REDACTED]", text
        )
        text = re.sub(r"/(?:home|Users)/[^\s\"<>]+", "[PRIVATE_PATH]", text)
        return text
