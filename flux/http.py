"""Bounded remote JSON input; reject encodings before HTTPX can inflate response bodies."""

import json
from typing import Any

import httpx

MAX_RESPONSE_BYTES = 1_000_000


async def bounded_json(response: httpx.Response) -> Any:
    # Callers request identity. Do not let a server force an unbounded decompressor.
    if response.headers.get("Content-Encoding", "identity").strip().lower() != "identity":
        raise ValueError("unexpected_content_encoding")
    length = response.headers.get("Content-Length")
    if length is not None and (
        not length.isascii() or not length.isdecimal() or int(length) > MAX_RESPONSE_BYTES
    ):
        raise ValueError("invalid_response_length")
    payload = bytearray()
    async for chunk in response.aiter_bytes(chunk_size=8192):
        if len(chunk) > MAX_RESPONSE_BYTES - len(payload):
            raise ValueError("response_too_large")
        payload.extend(chunk)
    try:
        return json.loads(payload)
    except RecursionError as exc:
        raise ValueError("invalid_remote_json") from exc
