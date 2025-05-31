"""Interactive console for Jupiter collateral testing."""

from typing import Optional
from rich.console import Console

from core.core_imports import configure_console_log, DB_PATH, log
from data.data_locker import DataLocker
from wallets.wallet_core import WalletCore

try:
    from solana.transaction import Transaction
    import base64
except Exception:  # pragma: no cover - optional dependency
    Transaction = None
    base64 = None

console = Console()
configure_console_log(debug=True)


def _select_wallet(core: WalletCore):
    wallets = core.load_wallets()
    log.debug("Wallets loaded", payload={"count": len(wallets)}, source="JupiterConsole")
    if not wallets:
        console.print("🚫 [red]No wallets found.[/red]")
        return None
    while True:
        console.print("\n👛 [bold]Available Wallets[/bold]")
        for idx, w in enumerate(wallets, start=1):
            console.print(f"{idx}) {w.name} ({w.public_address})")
        choice_str = console.input("👉 Select wallet (q to exit) > ").strip()
        log.debug("Wallet input", payload={"input": choice_str}, source="JupiterConsole")
        if choice_str.lower() in {"q", "exit"}:
            log.debug("Wallet selection aborted", source="JupiterConsole")

            return None
        try:
            choice = int(choice_str)
            if 1 <= choice <= len(wallets):

                selected = wallets[choice - 1]
                log.debug("Wallet selected", payload={"wallet": selected.public_address}, source="JupiterConsole")
                return selected
        except Exception as exc:
            log.debug("Parse failure", payload={"error": str(exc)}, source="JupiterConsole")

        console.print("[red]Invalid selection[/red]")


def _get_input(prompt: str, cast=float):
    try:
        value = cast(console.input(prompt).strip())
        log.debug("User input", payload={"prompt": prompt, "value": value}, source="JupiterConsole")
        return value
    except Exception as exc:
        log.debug("Invalid input", payload={"error": str(exc)}, source="JupiterConsole")
        console.print("🚫 [red]Invalid input[/red]")
        return None


def _maybe_send_tx(core: WalletCore, wallet, result: dict):
    msg = result.get("transaction") or result.get("message")
    log.debug("maybe_send_tx", payload={"has_msg": bool(msg)}, source="JupiterConsole")
    if not (msg and Transaction and base64):
        console.print("[yellow]No transaction payload returned.[/yellow]")
        return
    try:
        tx = Transaction.deserialize(base64.b64decode(msg))
        sig = core.send_transaction(wallet, tx)
        console.print(f"[green]Signature:[/green] {sig}")
        log.debug("Transaction sent", payload={"sig": sig}, source="JupiterConsole")
    except Exception as exc:
        log.debug("Transaction failed", payload={"error": str(exc)}, source="JupiterConsole")
        console.print(f"[red]Failed to sign/send: {exc}[/red]")


def deposit_flow(core: WalletCore):
    log.banner("💰 DEPOSIT COLLATERAL")
    wallet = _select_wallet(core)
    if not wallet:
        return
    market = console.input("🪙 Market symbol > ").strip()
    log.debug("Market entered", payload={"market": market}, source="JupiterConsole")
    amount = _get_input("💵 Amount > ")
    if amount is None:
        return
    result = core.deposit_collateral(wallet, market, amount)
    log.debug("Deposit result", payload={"result": result}, source="JupiterConsole")
    console.print(result)
    if result:
        _maybe_send_tx(core, wallet, result)


def withdraw_flow(core: WalletCore):
    log.banner("📤 WITHDRAW COLLATERAL")
    wallet = _select_wallet(core)
    if not wallet:
        return
    market = console.input("🪙 Market symbol > ").strip()
    log.debug("Market entered", payload={"market": market}, source="JupiterConsole")
    amount = _get_input("💵 Amount > ")
    if amount is None:
        return
    result = core.withdraw_collateral(wallet, market, amount)
    log.debug("Withdraw result", payload={"result": result}, source="JupiterConsole")
    console.print(result)
    if result:
        _maybe_send_tx(core, wallet, result)


def check_balance_flow(core: WalletCore):
    log.banner("💳 CHECK WALLET BALANCE")
    wallet = _select_wallet(core)
    if not wallet:
        return
    balance = core.fetch_balance(wallet)
    if balance is not None:
        console.print(f"💰 [green]{wallet.name}[/green] has [cyan]{balance:.4f} SOL[/cyan]")
    else:
        if core.client is None:
            console.print(
                "[yellow]Solana packages missing. Install them with:[/yellow]"
            )
            console.print("pip install solana==0.36.6 solders==0.26.0")
        console.print(f"🚫 [red]Could not fetch balance for {wallet.name}[/red]")


def main():
    DataLocker.get_instance(str(DB_PATH))  # ensure DB initialized
    core = WalletCore()
    while True:
        console.print("\n[bold cyan]Jupiter Collateral Console[/bold cyan]")
        console.print("1) 💰 Deposit Collateral")
        console.print("2) 📤 Withdraw Collateral")
        console.print("3) 💳 Check Wallet Balance")
        console.print("4) ❌ Exit")
        choice = console.input("Choose > ").strip()
        log.debug("Menu choice", payload={"choice": choice}, source="JupiterConsole")
        if choice == "1":
            deposit_flow(core)
        elif choice == "2":
            withdraw_flow(core)
        elif choice == "3":
            check_balance_flow(core)
        elif choice == "4":
            log.success("Console exited. Goodbye 👋", source="JupiterConsole")
            break
        else:
            console.print("[red]Invalid choice[/red]")


if __name__ == "__main__":
    main()
