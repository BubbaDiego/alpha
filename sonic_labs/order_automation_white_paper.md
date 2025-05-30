# Automating Perpetual Trading on Jupiter: Tools and Considerations

## Introduction and Context
Jupiter (a crypto trading platform) does not offer a public API for perpetuals trading, which means automation must simulate user interactions on the website. This involves using a web browser with a wallet extension (e.g. Phantom for Solana or MetaMask for EVM) to authenticate and sign transactions. The goal is to execute trades programmatically via the UI, using Python on the backend. Key requirements include:
- Automating complex perpetual swap operations (not just simple token swaps).
- Handling wallet-based logins and transaction confirmations via browser extensions.
- Running in both headless (no visible UI) and headed (full browser) modes as needed.
- Ensuring reliability and avoiding detection (since many sites deploy bot-detection measures).
- Keeping the solution manageable in a Python-centric environment (the backend and website are Python-based).

This report explores popular browser automation tools – Playwright, Puppeteer, Selenium, and others – comparing their capabilities in the context of this use case. We evaluate each in terms of ease of use, Python support, wallet extension integration, stealth (anti-bot evasion), and reliability, then recommend the best approach.

## Requirements and Challenges
Automating a dApp-like website with wallet authentication presents unique challenges:

1. **No Official API** – All interactions must be done through the web UI, mimicking a real user. This means clicking buttons, reading dynamic page data, and waiting for confirmation dialogs.
2. **Wallet Extension Interaction** – The automation must handle browser extension pop-ups for Phantom/MetaMask, including unlocking the wallet and approving transactions.
3. **Headless vs Headed Mode** – For server de[collateral_management_playwright_white_paper.md](collateral_management_playwright_white_paper.md)ployments, headless mode is desired. Newer Chrome allows extensions in headless mode using `--headless=new`.
4. **Bot Detection and Stealth** – Trading platforms may detect automated browsers. Stealth modes or plugins help avoid detection by modifying browser fingerprints.
5. **Session Persistence** – Reusing a persistent browser profile lets the wallet stay logged in, reducing friction.
6. **Reliability** – Because real funds are involved, the automation must be robust and handle timing issues gracefully.

## Automation Tools Overview
### Playwright (Python)
Playwright is a modern automation framework with first-class Python support. It can automate Chromium, Firefox, and WebKit.
- **Ease of Use** – Intuitive async API with auto-waiting built in.
- **Python Integration** – Official Python package, easily installed via pip.
- **Wallet Extension Support** – Can load extensions with a persistent context and supports headless mode with extensions.
- **Stealth** – Less detectable than Selenium by default; additional stealth plugins are available.
- **Reliability** – Actively maintained with powerful features like tracing and network interception.

### Puppeteer (with Python Wrappers)
Puppeteer is a Node.js library. In Python, one would use the unofficial Pyppeteer project.
- **Ease of Use** – Similar API to Playwright but Python wrappers lag behind in features.
- **Python Integration** – Unofficial; project maintenance is sporadic.
- **Wallet Extension Support** – Possible to load extensions, though headless support for extensions is experimental.
- **Stealth** – The Node ecosystem has the well-known `puppeteer-extra` stealth plugin; Python ports exist but are less mature.
- **Reliability** – Official Node version is stable, but the Python port may be outdated.

### Selenium (WebDriver)
Selenium is the long-standing tool for browser automation.
- **Ease of Use** – Requires more manual waits and handling window switching.
- **Python Integration** – Mature Python bindings with a large community.
- **Wallet Extension Support** – Supports extensions, though headless mode with extensions requires `--headless=new` and can be finicky.
- **Stealth** – Easily detected unless using patches like `undetected-chromedriver`.
- **Reliability** – Very stable for standard automation but can be brittle on dynamic apps.

## Comparison of Tools
| Tool                     | Ease of Use | Python Support | Wallet Extension Integration | Stealth Capabilities | Reliability |
|--------------------------|--------[test_db_portfolio_alert_toggle.py](../tests/test_db_portfolio_alert_toggle.py)-----|----------------|------------------------------|----------------------|-------------|
| **Playwright**           | High        | Excellent      | Good – persistent context with extensions; headless support | Moderate with plugins | Very high |
| **Puppeteer/Pyppeteer**  | Moderate    | Limited        | Fair – extensions supported but headless is experimental | High via puppeteer-extra (Node) | High (Node) / Medium (Python) |
| **Selenium**             | Moderate    | Great          | Fair – extensions load but pop-ups need manual handling | Low by default; use undetected-chromedriver | High |

Playwright offers the most straightforward path in a pure Python environment, balancing ease of use, extension support, and reliability.

## Recommended Approach
Use **Playwright with Python** for automating Jupiter perpetuals trading. Key reasons:
1. Seamless wallet integration via persistent contexts.
2. Support for headless operation with extensions.
3. Active maintenance and strong community.
4. Stealth can be enhanced with community plugins if necessary.

### Implementation Tips
- Configure a persistent browser profile with Phantom or MetaMask preloaded.
- Listen for new pages or pop-ups when the wallet asks for confirmation, then interact with those pages to approve transactions.
- Insert small random delays and mimic human actions to avoid detection.
- Handle errors and retries carefully – failed trades should trigger alerts.
- Keep the wallet extension version pinned to avoid breaking selectors.

## Conclusion
Automating Jupiter’s perpetual trading via the web UI requires careful browser automation. Playwright with Python provides the best mix of features and reliability, with workable solutions for wallet extensions and stealth. Selenium is an alternative if using `undetected-chromedriver`, while Puppeteer in Python is less appealing due to maintenance. With the outlined considerations, one can build a robust personal trading automation script that interacts with Jupiter just like a human user.
