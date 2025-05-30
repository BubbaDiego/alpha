# 🤖 Auto Core Specification

> Version: `v1.0`
> Author: `CoreOps 🥷`
> Scope: Browser automation for collateral management using Playwright.

---

## 📂 Module Structure
```txt
auto_core/
├── auto_core.py        # 🤖 High level Phantom automation
├── phantom_workflow.py # 🔮 Helper flows for wallet pop-ups
```

### 🤖 `AutoCore`
Central orchestrator for automating deposit and withdrawal flows via Jupiter's UI.

```python
AutoCore(
    phantom_path: str,
    profile_dir: str,
    headless: bool = False,
    *,
    extension_id: str | None = None,
    user_agent: str | None = None,
    slow_mo: int | None = None,
)
```
- `phantom_path`: path to the Phantom extension directory.
- `profile_dir`: folder for Playwright's persistent profile.
- `headless`: optional headless mode flag.
- `extension_id`: ID for the Phantom extension when running headless.
- `user_agent`: optional custom user agent.
- `slow_mo`: Playwright slow motion delay in ms.

**Key Methods**
- `_launch_context()` – Start Playwright with Phantom and open Jupiter. 【F:auto_core/auto_core.py†L17-L30】
- `deposit_collateral(amount: float)` – Fill deposit form and confirm Phantom pop‑ups. 【F:auto_core/auto_core.py†L37-L47】
- `withdraw_collateral(amount: float)` – Mirror of deposit flow for withdrawals. 【F:auto_core/auto_core.py†L49-L59】

### 🔮 `phantom_workflow` Helpers
- `connect_wallet(page)` – Clicks the Jupiter connect button then approves in Phantom. 【F:auto_core/phantom_workflow.py†L10-L18】
- `approve_popup(page)` – Confirms Phantom approval pop‑ups. 【F:auto_core/phantom_workflow.py†L21-L27】
- `confirm_transaction(page, timeout=30000)` – Waits for a Jupiter confirmation message. 【F:auto_core/phantom_workflow.py†L30-L32】

### ✅ Design Notes
- Reuses a persistent browser profile so Phantom stays logged in across runs.
- Wallet interactions are encapsulated in `phantom_workflow` functions.
- AutoCore focuses solely on UI automation and does not persist state or read from the database.
