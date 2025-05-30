Jupiter Perpetuals Integration Report
1. Overview
Jupiter Perpetuals (“Perps”) on Solana is a decentralized derivatives platform that—at the time of writing—lacks an official public API for programmatic trading. Instead, community developers and power users have reverse‐engineered parts of its functionality to interact with it either via UI automation (using tools such as Playwright with Solflare) or through direct on-chain transactions via the Anchor framework.

This report covers:

Wallet automation options: Phantom vs. Solflare vs. custom code.

UI Automation vs. On-Chain Integration: How to use Playwright for transaction approval and how to bypass the UI using an Anchor-based client.

Environment Setup: Installing Rust, Solana CLI, and Anchor CLI on Windows (or via WSL) and generating a wallet keypair.

Python-Based Client with AnchorPy: A step-by-step guide to creating a client that sends order requests to Jupiter Perps.

Key Account Addresses for Jupiter Perps (SOL): Unofficial but community-supported public keys and PDAs for the integration.

2. Automation-Friendly Wallet Options on Solana
Different Solana wallet solutions have varying levels of automation support:

Phantom:
The most popular wallet with a user-friendly interface. However, its browser extension poses challenges for automation due to constant pop-up approval modals.

Solflare:
A dedicated Solana wallet that offers an Auto-Approve mode for burner accounts. This feature is favorable for headless browser automation via Playwright, as it removes the manual confirmation steps, enabling faster transaction flows. (See BLOG.GOOSEFX.IO guides and DE.FI documentation for details.)

Backpack:
A newer, multi-chain wallet with developer hooks (e.g. deep links) and xNFT integrations. Although promising, it currently lacks built-in auto-confirmation, making it less ideal for immediate automation without further customization.

Custom Python SDK (e.g., using solana-py):
The most robust and automation-friendly solution is to bypass the GUI entirely by using on-chain keypair management. This means generating your wallet programmatically and signing transactions directly via RPC calls. (This is the approach pursued in the Anchor-based integration.)

3. UI Automation vs. Direct On-Chain Integration
UI Automation with Playwright (and Solflare)
Method: Automate browser interactions for actions such as connecting the wallet, selecting trading parameters, and confirming transactions.

Drawbacks:

Susceptible to UI changes (e.g. renaming of buttons, layout shifts).

Requires handling pop-ups and waiting for network events.

Example:
A script might click the Solflare extension’s “Connect” button, fill in trade details on a Jupiter webpage, then approve the transaction via auto-approve on a burner account.

Direct On-Chain Interaction using Anchor & AnchorPy
Method:
Use the Anchor framework’s client libraries to build and send Solana transactions directly, bypassing UI automation altogether.

Benefits:

Higher control and reliability.

Lower latency as you don’t rely on browser rendering.

Key Instruction Example:

typescript
Copy
await program.methods
  .createIncreasePositionMarketRequest({
    side,
    sizeUsdDelta,
    collateralTokenDelta,
    priceSlippage,
    jupiterMinimumOut: ... // computed via Jupiter’s Quote API if needed
  })
  .accounts({
    owner: walletPublicKey,
    pool: JLP_POOL_ACCOUNT_PUBKEY,
    custody: marketCustodyPubkey,
    collateralCustody: collateralCustodyPubkey,
    fundingAccount: userCollateralAccount,
    inputMint: collateralMint,
    perpetuals: [PDA for "perpetuals"]
    // ...other PDAs as required...
  })
  .signers([...])
  .rpc();
This direct method is implemented in our Python client sample using AnchorPy.

4. Environment Setup on Windows (or WSL)
Installing Rust, Solana CLI, and Anchor CLI
Rust:
Install using rustup:

bash
Copy
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
Then, add Rust to your environment by sourcing:

bash
Copy
source $HOME/.cargo/env
Solana CLI (Windows Native):
Download the installer via PowerShell:

powershell
Copy
iwr https://release.solana.com/v2.1.18/solana-install-init.exe -OutFile solana-install-init.exe
.\solana-install-init.exe
Verify with:

powershell
Copy
solana --version
solana-keygen --version
If using WSL, note that Windows paths must be translated (e.g. /mnt/c/Users/YourUsername/...).

Anchor CLI:
Install using Cargo:

bash
Copy
cargo install --git https://github.com/project-serum/anchor anchor-cli --locked
Verify:

bash
Copy
anchor --version
Generating and Setting Up Your Wallet Keypair
Generate a Keypair: On Ubuntu (WSL or native Linux), run:

bash
Copy
solana-keygen new --outfile ~/solana_keypair.json
Verify with:

bash
Copy
ls -l ~/solana_keypair.json
Update Solana Config:
Set the new keypair as default:

bash
Copy
solana config set --keypair ~/solana_keypair.json
Note: If you’re running from WSL but want to store on the Windows C: drive, use the /mnt/c/ prefix.

5. Python-Based Client Using AnchorPy
AnchorPy is the Python equivalent of Anchor’s client library. It allows you to load an IDL, create a Program instance, and call on-chain instructions directly.

Example Python Script (jupiter_order.py)
python
Copy
import json
import asyncio
from anchorpy import Provider, Program, Wallet, Context
from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from solana.publickey import PublicKey

async def main():
    # Load your wallet keypair from file
    with open("/home/bubba/solana_keypair.json", "r") as f:
        secret = json.load(f)
    wallet = Wallet(Keypair.from_secret_key(bytes(secret)))
    
    # Connect to Solana mainnet
    connection = AsyncClient("https://api.mainnet-beta.solana.com")
    provider = Provider(connection, wallet)
    
    # Load the Jupiter Perps IDL (assumed saved as 'jupiter_perps.json')
    with open("jupiter_perps.json", "r") as f:
        idl = json.load(f)
    
    # Set the unofficial Jupiter Perps program ID
    program_id = PublicKey("JUPP4eM8KuZVd6HzW9N1kS7PkKG2v9d9CcyAERqT1x6B")
    
    # Create the program instance
    program = Program(idl, program_id, provider)
    
    # Define parameters for a new position request (example values)
    side = 0  # 0 for long, 1 for short
    size_usd_delta = 100  # USD value for the position
    collateral_token_delta = 10  # Collateral amount (e.g., USDC)
    price_slippage = 1
    jupiter_minimum_out = 0
    
    # Define the required accounts
    # Replace the placeholders with actual addresses from community documentation:
    accounts = {
        "owner": wallet.public_key,
        "pool": PublicKey("5BUwFW4nRbftYTDMbgxykoFWqWHPzahFSNAaaaJtVKsq"),  # Jupiter Liquidity Pool
        "custody": PublicKey("7xS2gz2bTp3fwCC7knJvUWTEU9Tycczu6VhJYKgi1wdz"),  # SOL custody
        "collateralCustody": PublicKey("G18jKKXQwBbrHeiK3C9MRXhkHsLHf7XgCSisykV46EZa"),  # USDC custody
        "fundingAccount": PublicKey("<USER_COLLATERAL_ACCOUNT>"),  # User’s USDC associated token account
        "inputMint": PublicKey("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),  # Official USDC mint on Solana mainnet
        "perpetuals": PublicKey("<PERPETUALS_PDA>")  # Global PDA for Jupiter Perps (derive using seed “perpetuals”)
    }
    
    try:
        tx = await program.rpc["create_increase_position_market_request"](
            side,
            size_usd_delta,
            collateral_token_delta,
            price_slippage,
            jupiter_minimum_out,
            ctx=Context(accounts=accounts, signers=[])
        )
        print("Transaction successful! Signature:", tx)
    except Exception as e:
        print("Error creating position request:", e)
    
    await connection.close()

if __name__ == "__main__":
    asyncio.run(main())
How to Proceed
Dependencies:
Make sure you have installed anchorpy and solana Python packages.

IDL File:
Fetch the Jupiter Perps IDL using Anchor CLI if available:

bash
Copy
anchor idl fetch JUPP4eM8KuZVd6HzW9N1kS7PkKG2v9d9CcyAERqT1x6B > jupiter_perps.json
(Replace with the correct program ID if needed.)

Accounts:
The accounts provided above for the SOL market are based on community sources:
[jupiter_order.py](jupiter_order.[jupiter_order.py](jupiter_order.py)py)
JLP Pool Acc[jupiter_order.py](jupiter_order.py)ount: 5BUwFW4nRbftYTDMbgxykoFWqWHPzahFSNAaaaJtVKsq
**

Market Custo[jupiter_order.py](jupiter_order.py)dy (SOL): 7xS2gz2bTp3fwCC7knJvUWTEU9Tycczu6VhJYKgi1wdz
**

Collateral Custody (USDC): G18jKKXQwBbrHeiK3C9MRXhkHsLHf7XgCSisykV46EZa
**

Collateral Mint (USDC): EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
**

Perpetuals PDA: This is derived from the program ID with a fixed seed (typically “perpetuals”). You might need to compute it using Solana’s PublicKey.find_program_address method. Check community repos or Jupiter documentation for the exact value.

User Collateral Account: This is your associated token account for USDC, which can be derived using standard methods (the SPL Associated Token Account program).

Testing:
Initially test with small position sizes to verify that your transaction is created and that on-chain state is updated accordingly. Monitor the transaction signature using Solana Explorer.

6. Conclusion
This report outlines the steps to set up a Python-based client using AnchorPy to interact directly with Jupiter Perps on Solana mainnet. We covered:

The differences between UI automation and direct on-chain integration.

How to install and set up the required tools (Rust, Solana CLI, Anchor CLI, and Python libraries).

A step-by-step example Python script to send an order request, using community-sourced account addresses (for SOL and USDC) and the unofficial Jupiter Perps program ID (JUPP4eM8KuZVd6HzW9N1kS7PkKG2v9d9CcyAERqT1x6B).

Be sure to double-check and validate all account details from up-to-date community sources or Jupiter’s own announcements before going live.

Let me know if you need any more details or further adjustments, babie!

Citations:

- Jupiter Perps on-chain integration details

- Solana addresses and PDAs from community documentation

Additional community research from GitHub and developer forums as referenced in this report.

Happy coding, and good luck with your Jupiter orders, babie!