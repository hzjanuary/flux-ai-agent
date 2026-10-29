"""Untrusted HTTP input must be rejected before decoding/allocating an oversized body."""

import gzip
import json
from dataclasses import replace

import httpx
import pytest

from flux.errors import Denied, ProviderError
from flux.provider import OpenRouter
from flux.tools import Registry


class ProbeStream(httpx.AsyncByteStream):
    def __init__(self, payload: bytes):
        self.payload = payload
        self.started = False
        self.closed = False

    async def __aiter__(self):
        self.started = True
        yield self.payload

    async def aclose(self):
        self.closed = True


@pytest.mark.parametrize("adapter_name", ["provider", "search"])
@pytest.mark.parametrize("header", ["compressed", "oversized"])
async def test_untrusted_response_headers_rejected_before_body(
    settings, store, monkeypatch, adapter_name, header
):
    if header == "compressed":
        payload = gzip.compress(b"x" * 2_000_000)
        headers = {"Content-Encoding": "gzip"}
    else:
        payload = b"{}"
        headers = {"Content-Length": "1000001"}
    stream = ProbeStream(payload)

    def respond(request):
        assert request.headers["Accept-Encoding"] == "identity"
        return httpx.Response(200, headers=headers, stream=stream)

    config = replace(
        settings,
        provider_enabled=True,
        provider_key="synthetic-provider-key",
        web_enabled=True,
        web_key="synthetic-web-key",
    )
    transport = httpx.MockTransport(respond)
    if adapter_name == "provider":
        operation = OpenRouter(config, transport).complete([], config.model, 100, 5)
        error = ProviderError
    else:
        original = httpx.AsyncClient
        monkeypatch.setattr(
            httpx, "AsyncClient", lambda **kwargs: original(transport=transport, **kwargs)
        )
        operation = Registry(config, store)._search({"query": "fixture", "max_results": 1})
        error = Denied
    with pytest.raises(error):
        await operation
    assert not stream.started
    assert stream.closed


@pytest.mark.parametrize("adapter_name", ["provider", "search"])
async def test_identity_stream_accepts_valid_json_and_closes(
    settings, store, monkeypatch, adapter_name
):
    config = replace(
        settings,
        provider_enabled=True,
        provider_key="synthetic-provider-key",
        web_enabled=True,
        web_key="synthetic-web-key",
    )
    body = (
        {"choices": [{"message": {"content": "fixture answer"}, "finish_reason": "stop"}]}
        if adapter_name == "provider"
        else {"web": {"results": []}}
    )
    stream = ProbeStream(json.dumps(body).encode())

    def respond(request):
        assert request.headers["Accept-Encoding"] == "identity"
        return httpx.Response(200, stream=stream)

    transport = httpx.MockTransport(respond)
    if adapter_name == "provider":
        assert (
            await OpenRouter(config, transport).complete([], config.model, 100, 5)
            == "fixture answer"
        )
    else:
        original = httpx.AsyncClient
        monkeypatch.setattr(
            httpx, "AsyncClient", lambda **kwargs: original(transport=transport, **kwargs)
        )
        assert "UNTRUSTED WEB DATA" in await Registry(config, store)._search(
            {"query": "fixture", "max_results": 1}
        )
    assert stream.started and stream.closed


@pytest.mark.parametrize("adapter_name", ["provider", "search"])
async def test_response_without_declared_length_stops_at_byte_ceiling(
    settings, store, monkeypatch, adapter_name
):
    class EndlessStream(httpx.AsyncByteStream):
        chunks = 0
        closed = False

        async def __aiter__(self):
            for _ in range(200):
                self.chunks += 1
                yield b"x" * 8192
            raise AssertionError("Read beyond body limit")

        async def aclose(self):
            self.closed = True

    stream = EndlessStream()
    transport = httpx.MockTransport(lambda request: httpx.Response(200, stream=stream))
    config = replace(
        settings,
        provider_enabled=True,
        provider_key="synthetic-provider-key",
        web_enabled=True,
        web_key="synthetic-web-key",
    )
    if adapter_name == "provider":
        with pytest.raises(ProviderError, match="invalid_output"):
            await OpenRouter(config, transport).complete([], config.model, 100, 5)
    else:
        original = httpx.AsyncClient
        monkeypatch.setattr(
            httpx, "AsyncClient", lambda **kwargs: original(transport=transport, **kwargs)
        )
        with pytest.raises(Denied):
            await Registry(config, store)._search({"query": "fixture", "max_results": 1})
    assert stream.closed and stream.chunks == 123
