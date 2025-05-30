# Jupiter API Spec

Author: BubbaDiego
Date: 2025-05-24

## Overview

Managing collateral on Solana typically involves building and signing transactions that call on-chain program instructions. Using Python, you can leverage libraries like Solana-Py (the official Solana Python SDK) or AnchorPy (for Anchor framework programs) to compose and send these transactions. Below we outline approaches and examples for adding/removing collateral to an existing position, including swapping assets via Jupiter aggregator and calling deposit/withdraw instructions on lending/margin protocols.

### Python Tools and SDKs for Solana Transactions
- **Solana-Py** – A low-level Python SDK to construct transactions, create instructions, and interact with the Solana RPC API.
- **AnchorPy** – A Python client for Anchor-based Solana programs. With an IDL, AnchorPy lets you call Anchor program methods directly.
- **Solders** – A high-performance Python library providing types for advanced use cases.
- **Solathon** – An easy-to-use Python SDK (community) for Solana.
- **Protocol-specific SDKs** – Some Solana DeFi protocols provide Python SDKs such as DriftPy and Mango Explorer for collateral operations.

### Constructing and Sending a Transaction with Solana-Py
1. **Initialize RPC client and keypair(s).**
2. **Create instruction(s).**
3. **Add instruction(s) to a Transaction.**
4. **Fetch recent blockhash.**
5. **Sign the transaction.**
6. **Send the transaction.**

Example – Basic SOL Transfer:
```python
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer

client = Client("https://api.devnet.solana.com")
# Prepare a transfer instruction of 0.1 SOL from sender to receiver
instruction = transfer(TransferParams(
    from_pubkey=sender.public_key,
    to_pubkey=receiver_public_key,
    lamports=100_000_000
))
# Create transaction and sign
txn = Transaction().add(instruction)
client.send_transaction(txn, sender)
```

### Swapping Tokens via Jupiter Aggregator
Use Jupiter’s Quote API to get swap routes and incorporate resulting instructions into a Solana transaction. Example snippet:
```python
import requests, json
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey

amount_sol = 1.0
input_mint = "So11111111111111111111111111111111111111112"
output_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
client = Client("https://api.devnet.solana.com")
# Fetch swap route
url = f"https://quote-api.jup.ag/v6/quote?inputMint={input_mint}&outputMint={output_mint}&amount={int(amount_sol * 10**9)}&slippageBps=50"
quote_data = requests.get(url).json()
route_plan = quote_data.get("routePlan")
```
Add each instruction from `route_plan` into your transaction as `TransactionInstruction` objects, sign, and send.

### Adding Collateral Example (Anchor)
Using AnchorPy or Anchor in TypeScript, call Jupiter’s `increasePosition` instruction with `size_usd_delta = 0` and `collateral_delta` set to the deposit amount.

### Removing Collateral Example
Similarly, use the `decreasePosition` instruction with `size_usd_delta = 0` and `collateral_delta` representing the withdrawal amount.

### Account Structures
- **Position Account** – PDA derived from owner, custody accounts, etc.
- **PositionRequest Account** – Represents a pending action.
- **Custody Accounts** – Liquidity pool vaults for each token.
- **PositionRequest ATA** – Escrows tokens during deposit/withdrawal.

### Notes
- Deposits can be converted via Jupiter’s swap program if the token differs from the collateral token. Use `jupiter_minimum_out` to set slippage tolerance.
- Withdrawals similarly support conversion to another token before returning funds.
- Only one position per market per side is allowed.
- Ensure leverage remains within limits when withdrawing collateral.

This document summarizes how to manage collateral in Jupiter Perpetual positions using Solana transactions and available Python/Anchor SDKs.
