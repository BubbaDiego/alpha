# Dynamic Hedging and Gamma Scalping for Perpetual Futures

**Deprecated:** The `dynamic_hedging` strategy is no longer exposed in the UI but
the configuration file is retained for backward compatibility.

## Abstract
This white paper presents an in-depth exploration of dynamic delta hedging and gamma scalping strategies tailored for high-volatility cryptocurrency markets. Focusing on Bitcoin (BTC), Ethereum (ETH), and Solana (SOL) perpetual futures, we bridge theoretical models with practical execution techniques suited to near-term trading. Key concepts from options theory (e.g., delta-neutral positioning and gamma trading) are adapted to perpetual swap markets, emphasizing real-time adjustments and automated strategy implementation. We outline how an AI-driven “Oracle Core” system can integrate strategy logic, live position and market data, and user-defined risk profiles to actively manage exposure. Clearly defined sections cover relevant models, execution methods on crypto futures platforms (like Jupiter’s exchange), and tools for monitoring risk. The goal is to provide both a conceptual framework and actionable guidance—including example workflows, supporting tables, and diagrams—for implementing dynamic hedging and gamma scalping in an automated trading context.

## Introduction
Cryptocurrency markets are notoriously volatile and fast-paced, demanding equally dynamic risk management techniques. Dynamic hedging refers to continuously or frequently adjusting a portfolio’s positions to maintain a desired risk profile (often delta-neutral), thereby limiting directional exposure as market conditions change. Gamma scalping, traditionally an options strategy, involves maintaining a delta-neutral position and repeatedly rebalancing it to profit from the convexity (gamma) of an option’s payoff as the underlying asset’s price oscillates. In essence, gamma scalpers “buy low and sell high” on the underlying through continual hedging, capturing small gains from each price fluctuation while offsetting directional risk. These approaches are well-established in traditional markets, but this paper examines their application to cryptocurrency perpetual futures for BTC, ETH, and SOL—contracts that resemble futures without expiry and trade on exchanges 24/7. Adapting gamma-centric strategies to crypto futures requires careful consideration of market specifics. Unlike a classic option, a perpetual future has linear payoff (no inherent gamma), yet traders can still simulate “long gamma” behavior through volatility-driven trading tactics. For instance, by simultaneously holding long and short positions in related contracts—or on different platforms—one can construct a delta-neutral stance and then actively rebalance as prices move. The goal is to profit from short-term price swings (realized volatility) without betting on a single directional trend. In the high-volatility environment of BTC, ETH, and SOL, such volatility scalping can be especially profitable if executed correctly—but it also demands robust risk controls and near-real-time responsiveness.

**Figure: Oracle Core Dynamic Hedging System** – The development of an “Oracle Core” system is envisioned to automate these strategies. This core takes three primary inputs:
1. **Strategy logic** – the rules and models for hedging and scalping.
2. **Current position & market conditions** – real-time prices, volatility, and exposures.
3. **User-defined risk/reward profile** – parameters that describe risk tolerance and objectives.

An AI-driven engine combines strategy models with live data and user risk preferences to recommend or execute hedge adjustments. By encoding expert logic and real-time analytics, such an engine (potentially powered by GPT-based bots or other AI) can dynamically adjust positions to maintain a desired risk profile while seizing short-term opportunities. The following sections provide the foundation for building this system, from theoretical models to practical implementation details.

## Background: Dynamic Hedging and Gamma Scalping in Crypto
### Dynamic Delta Hedging
Dynamic hedging involves regularly rebalancing a position to offset changes in market exposure. A common example is delta hedging an options portfolio: as the underlying asset’s price moves, the option’s delta (sensitivity to price) changes, so the trader must buy or sell the underlying to maintain a delta-neutral stance. In crypto markets, dynamic hedging is vital because of rapid price swings and volatility regime shifts. For instance, an options market maker in BTC may start the day delta-neutral, but a sudden 5% jump in BTC’s price will leave them with a sizable delta exposure unless they quickly trade futures or spot to re-neutralize. The faster and more unpredictable the market (and crypto is both), the more critical it is to monitor and adjust hedges in real-time.

Several factors distinguish dynamic hedging in crypto from traditional markets:
- **24/7 Trading and Gaps:** Crypto trades around the clock on global venues. There are no market closes, which eliminates overnight gaps seen in equities—yet large jumps can occur at any time. Hedging systems must therefore operate continuously and possibly autonomously.
- **High Volatility and Tail Risks:** BTC and ETH often exhibit annualized volatility in the 60–100%+ range, with SOL sometimes even higher. Sudden double-digit percentage moves in minutes are not unheard of. This stochastic volatility means hedge ratios can become outdated quickly. A spike in implied volatility will alter option deltas and gammas, requiring more frequent rebalancing to stay neutral. Traders may incorporate volatility forecasts or dynamic models to anticipate these changes.
- **Market Liquidity and Slippage:** Liquidity varies across assets and venues. BTC perps are extremely liquid on major exchanges, while SOL perps might have higher spreads and lower depth. Dynamic hedging strategies must account for execution costs—every hedge trade incurs fees and potential slippage. Over-trading can erode profits.
- **Funding Rates and Carry:** Perpetual futures introduce funding payments—periodic cash flows between longs and shorts to tether the contract price to spot. These funding rates can be significant in volatile periods or when sentiment skews heavily bullish or bearish. A dynamic hedge in perps should monitor funding as part of its P&L. Traders can exploit funding differentials while remaining hedged.

### Gamma Scalping Fundamentals
Gamma scalping is traditionally executed by options market makers or volatility traders. The trader starts with a long gamma position (typically via a straddle) and delta hedges that position continuously. Being “long gamma” means the trader profits from volatility: as the underlying price moves, the option’s delta changes, prompting rebalancing by selling or buying the underlying to stay neutral. The effect is that the trader sells high and buys low, locking in small gains from each oscillation. However, maintaining the long option position comes at a cost—theta decay—and potentially financing costs. The hedging profits must exceed these costs for the strategy to be net profitable.

In crypto, gamma scalping can be pursued with options and futures or using perpetual futures only (volatility scalping). Even without options, one can emulate long gamma by holding equal long and short perp positions (often across venues) and trading around them as price oscillates. The strategy profits from realized volatility and, when structured carefully, from positive funding differentials. Risk management is essential, as persistent trends can lead to losses when repeatedly fading the move.

## Models for Dynamic Hedging in High-Volatility Crypto Markets
### Black-Scholes vs. Stochastic Volatility Models
The classic Black-Scholes model provides a baseline for delta-gamma-neutral hedging but assumes constant volatility. Crypto markets display stochastic volatility and jumps, making models like Heston or jump-diffusion more appropriate. Research on BTC options shows that incorporating stochastic volatility improves hedging performance, implying traders should update hedge ratios as implied volatility shifts.

### Delta-Gamma-Vega Hedging
Advanced tactics hedge not only delta but also higher-order Greeks like vega when possible. In crypto, vega hedging may involve offsetting positions in other options or futures. Liquidity constraints often make delta-gamma hedging the focus, while vega is managed by limiting position size or using volatility swaps.

### Dynamic Hedging with AI/ML
Machine learning methods, such as reinforcement learning, can optimize when to rebalance a hedge given transaction costs and market microstructure. Predictive models (e.g., LSTMs) can anticipate volatility spikes or price jumps, prompting pre-emptive hedges. An adaptive, data-driven approach helps keep hedging effective amid crypto’s turbulent conditions.

A sample workflow might include:
1. **Start-of-Day Calibration** – set initial hedge ratios using current implied volatilities and positions.
2. **Live Monitoring** – track price moves, IV changes, and liquidity metrics in real time.
3. **Rebalancing Logic** – use time- or event-driven triggers to decide when rehedging is warranted.
4. **Execution of Hedge Trades** – place market or limit orders via APIs, potentially splitting large orders to reduce impact.
5. **Post-Trade Evaluation** – update delta/gamma exposures and record P&L.
6. **End-of-Day Analysis** – review performance to refine thresholds and models.

## Execution Strategies for Perpetual Futures Markets
Implementing dynamic hedges and gamma scalps on perpetual futures requires efficient execution techniques and an understanding of market microstructure.

- **Order Types and Market Impact:** Decide between limit and market orders based on urgency and market conditions. For routine rebalancing, limits reduce costs; for urgent hedging, market orders guarantee execution.
- **Automation and Latency:** Bots running close to exchange servers execute hedges quickly. WebSocket data feeds and smart order routing help minimize delays and slippage.
- **Position Management and Edge Cases:** Monitor margin usage, funding payments, and exchange-specific halts or circuit breakers. Include fail-safes for disconnections or abnormal conditions.
- **Example Execution Flow:** Detect a delta imbalance, check liquidity, choose order type, execute the hedge, and confirm neutrality. Repeat as price moves.
- **Slippage and Trade Monitoring:** Track execution quality by logging expected vs. actual fill prices. Use this data to optimize order sizing, timing, and routing.

### Table: Tools and Indicators for Dynamic Hedging
| Indicator / Tool                | Role in Hedging                                      | Usage Example |
|---------------------------------|------------------------------------------------------|---------------|
| Implied Volatility (IV) & DVOL  | Gauge expected volatility to adjust hedging frequency | Tighten hedge intervals when IV spikes |
| Realized Volatility (RV)        | Compare recent price swings against IV               | Maintain or increase gamma exposure if RV > IV |
| Liquidity Metrics               | Monitor volume, open interest, and order book depth  | Choose the most liquid venue or contract for hedging |
| Funding Rates                   | Reflect carry cost/benefit for perp positions        | Capture positive funding while neutral |
| Position Greeks & P&L Monitors  | Track delta, gamma, theta, and running profits       | Alert if delta strays or P&L turns negative |
| Automated Execution Algorithms  | Bots and smart order routers for fast, low-cost trades | Split orders across venues to minimize impact |

## Practical Implementation and AI Integration
An implementation might use a Python stack with API libraries (e.g., ccxt), websockets for real-time data, and libraries such as `py_vollib` for option Greeks. Backtesting frameworks (Backtrader, QuantConnect) help refine strategy parameters. Deployment involves a resilient bot that runs 24/7, handles API reconnections, and logs every action.

**Example Hedging Bot Loop (Pseudocode)**
```python
while True:
    price = get_current_price("BTC-PERP")
    position = get_current_position("BTC-PERP")
    delta = position.delta()
    if abs(delta) > DELTA_THRESHOLD:
        order_size = -delta
        if market_volatility_high():
            execute_order("BTC-PERP", order_size, type="market")
        else:
            execute_order("BTC-PERP", order_size, type="limit")
    if time_to_recalc_greeks():
        update_option_greeks()
    pnl = calculate_strategy_pnl()
    sleep(SHORT_INTERVAL)
```
The Oracle Core can incorporate AI decision-making—GPT models may analyze the current state and output hedging recommendations or adjustments to parameters. User-defined personas and risk profiles guide how **degen** or **cautious** the system behaves. Real-time dashboards monitor delta, funding, and P&L, with alerts for anomalies or failures.

## Conclusion
Dynamic hedging and gamma scalping are powerful techniques for managing and profiting from volatility in crypto markets. By staying delta-neutral and continually adjusting to price moves, traders can capture short-term oscillations while limiting directional exposure. In perpetual futures, these strategies revolve around exploiting realized volatility and funding differentials. The integration of AI-driven tools—the Oracle Core concept—offers adaptive, automated execution that keeps pace with 24/7 market dynamics. With proper risk controls, monitoring, and technology, dynamic hedging and gamma scalping can turn crypto volatility into a steady source of returns.

## Sources
- Samyukta N. *Gamma Scalping with Perpetuals: A Volatility-Based Strategy for Traders.* Demex Blog – Sep 16, 2024.
- Amberdata Research. *Dynamic Hedging in Crypto: Strategies for Real-Time Risk Adjustment.* Amberdata Blog – Jan 3, 2025.
- Y.-C. Chang, H.-W. Teng, W. Härdle. *Stochastic volatility dynamic hedging for Deribit BTC options.* J. of Futures and Options 16(2), 2023.
- QuestDB. *Gamma Scalping Strategies – Glossary Entry.* QuestDB Blog, 2023.
- Rich Excell. *Delta Hedging and Gamma Scalping using Micro Bitcoin Options.* CME Group – Excell with Options (Newsletter), Apr 5, 2022.
- Arthur Hayes. *How to Mark[dynamic_hedging.json](../oracle_core/strategies/dynamic_hedging.json)et Make Bitcoin Derivatives – Lesson 1: Dynamic Hedging.* BitMEX Blog, 2016.
- ZtraderAI. *Gamma Scalping & Reverse Scalping: Strategies for Volatility Traders.* Medium, Dec 28, 2024.
- Alpaca Engineering. *Gamma Scalping: Building an Options Strategy with Python.* Alpaca Markets Blog, Nov 29, 2024.
