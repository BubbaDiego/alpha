# test_engine_confirm.py

from order_core.order_engine import OrderEngine
from order_core.order_broker import JupiterBroker

class DummyLocator:
    async def wait_for(self, state, timeout):
        print(f"🔍 [wait_for] state='{state}' within {timeout}ms")

    async def click(self, timeout):
        print(f"🖱️ [click] with timeout={timeout}ms")

class DummyPage:
    def locator(self, selector):
        print(f"🎯 Locator called with: {selector}")
        return DummyLocator()

    async def inner_html(self, selector):
        return "<html><body><button>Long SOL</button></body></html>"

class DummyAgent:
    def __init__(self):
        self.page = DummyPage()

def main():
    print("🔧 Creating test OrderEngine instance with mock page...")

    agent = DummyAgent()
    broker = JupiterBroker()
    engine = OrderEngine(agent=agent, broker=broker)

    engine.order_definition["position_type"] = "long"
    engine.order_definition["asset"] = "SOL"

    import asyncio
    asyncio.run(engine.confirm_order())

if __name__ == "__main__":
    main()
