# Automating Collateral Management on Jupiter (Solana) with Playwright and Phantom

## Introduction and Context
Jupiter is a leading Solana DEX aggregator that recently introduced perpetual futures. Traders must deposit collateral on-chain before opening leveraged positions. Deposits and withdrawals are handled through Jupiter's web interface with the Phantom wallet for signing transactions. Automating these flows requires browser control, wallet extension handling, support for both headed and headless modes, and a stealthy, reliable approach.

This white paper outlines how to use Playwright in Python to automate collateral deposit and withdrawal on Jupiter while integrating the Phantom wallet extension. The focus is on simulating real user interactions rather than crafting transactions directly in code.

## Requirements and Challenges for Collateral Automation
- **Wallet Interaction**: Phantom pop‑ups must be controlled to approve connections and sign transactions.
- **Workflow**: Navigate Jupiter's UI, input deposit/withdrawal amounts, trigger the on-chain transaction, and verify the resulting balance change.
- **Headed vs Headless Execution**: Chrome must load the Phantom extension in both modes using persistent contexts and appropriate flags.
- **Stealth**: Use realistic user agents and human‑like delays to avoid detection.
- **Reliability**: Wait for page events and confirmations to prevent flaky behavior.
- **Security**: Keep the private key within Phantom; the script only interacts via the extension.
[cyclone_app.py](../cyclone_app.py)
## Playwright Setup with Phantom Wallet Extension
Use a persistent Chromium context with the Phantom extension loaded:
```python
from playwright.sync_api import sync_playwright
[launch_pad.py](../launch_pad.py)
phantom_path = "/path/to/p[launch_pad.py](../launch_pad.py)hantom"
profile_dir = "/tmp/playwright/phantom-profile"

with sync_playwright() as pw:
    context = pw.chromium.launch_persistent_context(
        profile_dir,[launch_pad.py](../launch_pad.py)
        channel="chromium",
        headless=False,
        args=[
            f"--disable-extensions-except={phantom_path}",
            f"--load-extension={phantom_path}"
        ]
    )
    page = context.new_page()
    page.goto("https://jup.ag/perps")
```
The persistent profile retains Phantom's state so the wallet stays installed and unlocked across runs.

## Headed vs Headless Mode Considerations
- **Headed**: Phantom's approval UI appears as a normal popup window that Playwright can capture with `expect_page()`.
- **Headless**: Modern Chromium allows extensions in headless mode (`--headless=new`). You may need to open `chrome-extension://<ID>/popup.html` manually to display Phantom's UI.
- **Debugging**: Use headed mode during development; switch to headless in CI environments.

## Simulating Collateral Deposit & Withdrawal Workflows
1. Navigate to Jupiter and connect the wallet. Wait for the Phantom popup and approve the connection.
2. Enter the collateral amount and click **Deposit** (or **Withdraw**). Use Playwright's waiting features to catch the resulting Phantom approval page.
3. Approve the transaction in Phantom and wait for Jupiter's UI to confirm the balance change.
4. Handle errors and retries gracefully, ensuring the automation does not submit multiple transactions by accident.

## Technical Techniques for Stealth & Reliability
- Suppress automation flags and set a realistic user agent.
- Add small random delays between actions or use Playwright's slow-motion option.
- Favor Playwright's waits (`wait_for_selector`, `expect_page`) over fixed sleeps.
- Reuse wallet state via the persistent profile, but clean up collateral between runs as needed.

## Example and Reference Implementations
Community projects such as Dynamic Labs' wallet testing example and the Synpress framework demonstrate Playwright driving Phantom for Solana dApps. These serve as references for handling wallet extensions, pop‑ups, and transactions in automated tests.

## Conclusion
Playwright with the Phantom extension enables reliable automation of collateral management on Jupiter. By carefully handling wallet pop‑ups, supporting headless and headed modes, and incorporating stealth techniques, you can programmatically deposit and withdraw collateral while mimicking a real user. This approach provides a powerful tool for testing or operational bots that need to manage collateral on Solana without exposing private keys.

## References and Further Reading
- Playwright documentation on persistent contexts and Chrome extension support.
- Scrapfly articles on headless extensions and user agent considerations.
- Dynamic Labs E2E testing repository showing Phantom automation.
- Synpress announcement of Phantom wallet support.
