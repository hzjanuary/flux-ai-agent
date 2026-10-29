import pytest

from flux.errors import Denied
from flux.fs import RuntimeLock


def test_second_runtime_is_refused_and_released_after_close(tmp_path):
    root = tmp_path / "data"
    first = RuntimeLock(root)
    try:
        with pytest.raises(Denied):
            RuntimeLock(root)
    finally:
        first.close()
    second = RuntimeLock(root)
    second.close()


async def test_direct_switch_uses_same_budget_and_safe_tools(build):
    dispatcher, model, _, agent = build("NEED_TOOLS", "resolved answer", max_calls=2)
    from flux.telegram import Update

    assert await dispatcher.handle(Update(42, 42, 1, "hello")) == "resolved answer"
    assert len(model.calls) == agent.metrics["calls"] == 2
    assert "Available tools" not in model.calls[0]["messages"][0]["content"]
    assert "Available tools" in model.calls[1]["messages"][0]["content"]


async def test_web_route_discloses_before_any_model_or_network(build):
    dispatcher, model, _, agent = build(web_enabled=True, web_key="synthetic-key")
    from flux.telegram import Update

    reply = await dispatcher.handle(Update(42, 42, 1, "latest news"))
    assert "APPROVAL" in reply and "latest news" in reply
    assert not model.calls and agent.metrics["path"] == "web"
