import sys
import types
import pytest

from order_core.order_engine import OrderEngine
from order_core.order_model import OrderModel


class DummyLocator:
    def __init__(self, selector, page):
        self.selector = selector
        self.page = page

    @property
    def first(self):
        return self

    async def click(self, timeout=None):
        self.page.events.append(("click", self.selector, timeout))

    async def wait_for(self, state=None, timeout=None):
        self.page.events.append(("wait_for", self.selector, state, timeout))


class DummyPage:
    def __init__(self):
        self.events = []

    async def click(self, selector):
        self.events.append(("click", selector, None))

    async def fill(self, selector, value):
        self.events.append(("fill", selector, value))

    def locator(self, selector):
        return DummyLocator(selector, self)

    async def evaluate(self, script):
        self.events.append(("evaluate", script))

    async def wait_for_timeout(self, ms):
        self.events.append(("wait_for_timeout", ms))


class DummyAgent:
    def __init__(self):
        self.page = DummyPage()
        self.popup = None
        self.connected_url = None
        self.open_popup_called = False

    async def connect_wallet(self, dapp_url):
        self.connected_url = dapp_url

    async def open_popup(self):
        self.open_popup_called = True
        self.popup = DummyPage()
        return self.popup


def get_clicks(page, selector):
    return [ev for ev in page.events if ev[0] == "click" and ev[1] == selector]


@pytest.mark.asyncio
async def test_select_position_type():
    agent = DummyAgent()
    engine = OrderEngine(agent=agent, broker=None)
    await engine.select_position_type("long")
    assert get_clicks(agent.page, "button:has-text('Long')")
    assert engine.order_definition["position_type"] == "long"


@pytest.mark.asyncio
async def test_select_order_type():
    agent = DummyAgent()
    engine = OrderEngine(agent=agent, broker=None)
    await engine.select_order_type("limit")
    assert get_clicks(agent.page, "button:has-text('Limit')")
    assert engine.order_definition["order_type"] == "limit"


@pytest.mark.asyncio
async def test_select_asset():
    agent = DummyAgent()
    engine = OrderEngine(agent=agent, broker=None)
    await engine.select_asset("SOL")
    assert get_clicks(agent.page, "button:visible:has-text('SOL')")
    assert engine.order_definition["asset"] == "SOL"


@pytest.mark.asyncio
async def test_select_collateral_asset():
    agent = DummyAgent()
    engine = OrderEngine(agent=agent, broker=None)
    await engine.select_collateral_asset("USDC")
    assert engine.order_definition["collateral_asset"] == "USDC"


@pytest.mark.asyncio
async def test_set_position_size():
    agent = DummyAgent()
    engine = OrderEngine(agent=agent, broker=None)
    await engine.set_position_size("1.23")
    assert ("fill", "input[placeholder='0.00']", "1.23") in agent.page.events
    assert engine.order_definition["position_size"] == 1.23


@pytest.mark.asyncio
async def test_set_leverage():
    agent = DummyAgent()
    engine = OrderEngine(agent=agent, broker=None)
    await engine.set_leverage("2.1x")
    clicks = get_clicks(agent.page, "button:has-text('+')")
    assert len(clicks) == 10
    assert engine.order_definition["leverage"] == 2.1


@pytest.mark.asyncio
async def test_confirm_order():
    agent = DummyAgent()
    engine = OrderEngine(agent=agent, broker=None)
    await engine.confirm_order()
    assert any(ev[0] == "evaluate" for ev in agent.page.events)


@pytest.mark.asyncio
async def test_confirm_wallet_transaction():
    agent = DummyAgent()
    engine = OrderEngine(agent=agent, broker=None)
    await engine.confirm_wallet_transaction()
    assert agent.open_popup_called is True
    wait_events = [ev for ev in agent.popup.events if ev[0] == "wait_for"]
    click_events = get_clicks(agent.popup, "div[role='dialog'] button:has-text('Confirm')")
    assert wait_events
    assert click_events


@pytest.mark.asyncio
async def test_place_tp_sl_limit_order(monkeypatch):
    agent = DummyAgent()
    engine = OrderEngine(agent=agent, broker=None)
    captured = {}

    def fake_place_tp_sl_order(**kwargs):
        captured.update(kwargs)
        return "ok"

    monkeypatch.setitem(sys.modules, "tp_sl_helper", types.SimpleNamespace(place_tp_sl_order=fake_place_tp_sl_order))

    result = await engine.place_tp_sl_limit_order("AAA", "BBB", 1, 2, "key")
    assert result == "ok"
    assert captured == {
        "private_key_base58": "key",
        "input_mint": "AAA",
        "output_mint": "BBB",
        "in_amount": 1,
        "out_amount": 2,
    }


@pytest.mark.asyncio
async def test_get_order_builds_model():
    agent = DummyAgent()
    engine = OrderEngine(agent=agent, broker=None)
    await engine.select_asset("SOL")
    await engine.select_position_type("long")
    await engine.select_collateral_asset("SOL")
    await engine.set_position_size("1.5")
    await engine.set_leverage("2.0x")
    await engine.select_order_type("market")

    order = engine.get_order()
    assert isinstance(order, OrderModel)
    assert order.asset == "SOL"
    assert order.position_type == "long"
    assert order.collateral_asset == "SOL"
    assert order.position_size == 1.5
    assert order.leverage == 2.0
    assert order.order_type == "market"
    assert order.status == "pending"

