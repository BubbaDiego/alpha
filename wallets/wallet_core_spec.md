# 💼 Wallet Core Specification

> Version: `v1.0`
> Author: `CoreOps 🥷`
> Scope: WalletCore orchestrator and supporting wallet services.

---

## 📂 Module Structure
```txt
wallets/
├── wallet_core.py               # 🤝 High-level blockchain helper
├── wallet_service.py            # 📋 CRUD operations
├── wallet_repository.py         # 💾 Persistence layer
├── blockchain_balance_service.py # 🌐 Chain balance fetcher
├── jupiter_service.py           # 🔄 Jupiter Perps HTTP client
```

### 🤝 `WalletCore`
Central access point for wallet operations and Jupiter collateral management.

```python
WalletCore(rpc_endpoint="https://api.mainnet-beta.solana.com")
```

- `load_wallets()` returns all wallets and refreshes each balance. 【F:wallets/wallet_core.py†L52-L60】
- `set_rpc_endpoint()` switches RPC host and reinitializes the client. 【F:wallets/wallet_core.py†L62-L66】
- `fetch_balance()` obtains the SOL balance via the active RPC. 【F:wallets/wallet_core.py†L71-L80】
- `send_transaction()` signs and submits a transaction with the wallet keypair. 【F:wallets/wallet_core.py†L94-L108】
- `deposit_collateral()` posts an increase request through `JupiterService`. 【F:wallets/wallet_core.py†L113-L124】
- `withdraw_collateral()` posts a decrease request to Jupiter. 【F:wallets/wallet_core.py†L126-L136】

### ✅ Design Notes
- Uses `WalletService` for create/update/delete operations.
- `BlockchainBalanceService` handles ETH and Solana balance lookups.
- `JupiterService` wraps collateral API calls.
- All logging goes through the shared logger in `core.logging`.

### Open Questions ❓
- 🔒 Should private keys be encrypted at rest or stored externally?
- 🌐 Is multi-chain support beyond Solana planned for deposit/withdraw?
- 🛠️ Should WalletCore expose event hooks for UI updates?
