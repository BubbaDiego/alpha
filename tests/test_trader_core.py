from trader_core.trader_core import TraderCore

class DummyDataLocker:
    wallets = None
    def __init__(self):
        self.wallets = type('WalletMock', (), {
            'get_wallet_by_name': lambda self, name: {'name': name}
        })()
    def __getattr__(self, name):
        return lambda *args, **kwargs: {}

# Dummy persona manager with 1 persona
class DummyPersonaManager:
    def get(self, name):
        return type('Persona', (), {
            'name': name,
            'avatar': '',
            'profile': name,
            'origin_story': '',
            'risk_profile': '',
            'moods': {'stable': 'neutral'},
            'strategy_weights': {}
        })()
    def list_personas(self):
        return ['TestBot']

# Dummy strategy manager
class DummyStrategyManager:
    pass

if __name__ == "__main__":
    core = TraderCore(
        data_locker=DummyDataLocker(),
        persona_manager=DummyPersonaManager(),
        strategy_manager=DummyStrategyManager()
    )
    trader = core.create_trader("TestBot")
    print(trader)
