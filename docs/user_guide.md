📄 FILE 32: docs/user_guide.md

```markdown
# 📖 MARDUK-TRADING-RIG™ - USER GUIDE

**Version:** 1.0.0  
**Author:** Seliim Ahmed  
**Email:** amit.khanna.1082@gmail.com  
**Copyright:** © 2026 Seliim Ahmed. All Rights Reserved.

---

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Quick Start](#quick-start)
5. [Dashboard Guide](#dashboard-guide)
6. [Trading Guide](#trading-guide)
7. [Backtesting](#backtesting)
8. [Risk Management](#risk-management)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

---

## 📌 Introduction

MARDUK-TRADING-RIG™ is a proprietary trading engine that combines **3-6-9 Energy Flow**, **Fibonacci Probability**, and **Macro-Quantamental** analysis to generate high-probability trading signals.

### Key Features

- ✅ **3-6-9 Energy Flow Detection** - Captures market nodes at 3:00, 6:00, and 9:00
- ✅ **Fibonacci Probability Matrix** - Calculates probability of hitting golden zones
- ✅ **Macro-Quantamental Integration** - Weighs global economic indicators
- ✅ **Real-time Signal Generation** - Live trading signals with confidence levels
- ✅ **Risk Management** - Position sizing, stop loss, and drawdown protection
- ✅ **Backtesting Engine** - Historical performance analysis
- ✅ **Live Dashboard** - Real-time monitoring and control

---

## 🔧 Installation

### Prerequisites

- **Python 3.10+**
- **MetaTrader 5** (for live trading)
- **Git** (for cloning)

### Step 1: Clone the Repository

```bash
git clone https://github.com/Khan-Amit/marduk-trading-rig.git
cd marduk-trading-rig
```

Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Step 3: Configure Settings

```bash
cp config/settings.example.json config/settings.json
# Edit config/settings.json with your preferences
```

Step 4: Configure MetaTrader 5 (Optional)

```bash
# Install MetaTrader5 package
pip install MetaTrader5

# Configure your MT5 credentials in config/settings.json
```

---

⚙️ Configuration

config/settings.json

```json
{
    "trading": {
        "symbols": ["GBPUSD", "EURUSD", "USDJPY"],
        "timeframe": "M1",
        "max_positions": 5,
        "risk_per_trade": 0.02
    },
    "risk": {
        "min_stop_pips": 20,
        "max_stop_pips": 200,
        "min_risk_reward": 1.5,
        "target_risk_reward": 2.0,
        "max_drawdown": 0.20
    },
    "mt5": {
        "login": null,
        "password": null,
        "server": null
    }
}
```

Key Settings

Setting Description Default
symbols Trading symbols ["GBPUSD", "EURUSD", "USDJPY"]
timeframe Timeframe "M1"
max_positions Max concurrent positions 5
risk_per_trade Risk per trade (%) 0.02
min_stop_pips Minimum stop loss (pips) 20
max_stop_pips Maximum stop loss (pips) 200
target_risk_reward Target R/R ratio 2.0
max_drawdown Max drawdown limit 0.20

---

🚀 Quick Start

Start the Trading Engine

```bash
# Analysis mode
python main.py --mode analyze --symbol GBPUSD

# Live trading mode
python main.py --mode live --symbol GBPUSD --timeframe M1

# Backtest mode
python main.py --mode backtest --symbol GBPUSD --timeframe H1

# Dashboard mode
python main.py --mode dashboard
```

Dashboard Access

Once dashboard is running, open your browser:

```
http://localhost:8080
```

---

📊 Dashboard Guide

Overview

The dashboard provides real-time monitoring and control:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MARDUK-TRADING-RIG™ - DASHBOARD                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐  ┌─────────────────────────────────────────────┐   │
│  │ 💰 ACCOUNT SUMMARY  │  │ 🎯 TRADING SIGNAL                           │   │
│  │ Balance: $10,000.00 │  │ Action: BUY (Confidence: 72%)              │   │
│  │ Equity: $10,200.00  │  │ Entry: 1.32190 | SL: 1.31990 | TP: 1.32490│   │
│  │ P&L: +$200.00       │  │ R/R: 2.0                                   │   │
│  └─────────────────────┘  └─────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────┐  ┌─────────────────────────────────────────────┐   │
│  │ ⚡ 3-6-9 ENERGY FLOW │  │ 📈 FIBONACCI PROBABILITY                   │   │
│  │ 3:00 🟢 6:00 ⚪ 9:00 │  │ 23.6%: 45%  38.2%: 55%                   │   │
│  │ Confluence: C12     │  │ 50.0%: 60%  61.8%: 72%  78.6%: 48%        │   │
│  └─────────────────────┘  └─────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 📋 OPEN POSITIONS                                                    │   │
│  │ GBPUSD | BUY | 0.1 | 1.32190 | 1.32250 | +$60.00                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 📡 TERMINAL                                                          │   │
│  │ > 14:32:15 · Signal generated: BUY (Confidence: 72%)              │   │
│  │ > 14:32:16 · Order executed: BUY 0.1 GBPUSD @ 1.32190            │   │
│  │ > 14:32:30 · Position closed: +$60.00                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

📈 Trading Guide

Signal Interpretation

Signal Meaning
BUY Strong confluence indicating upward momentum
SELL Strong confluence indicating downward momentum
WATCH Moderate confluence - monitor for entry
HOLD No clear signal - wait

Confidence Levels

Confidence Meaning
> 70% High probability trade
50-70% Moderate probability
< 50% Low probability - avoid

Risk-Reward Ratios

Ratio Assessment
> 2.0 Excellent
1.5-2.0 Good
< 1.5 Poor - avoid

---

🔬 Backtesting

Run a Backtest

```bash
python main.py --mode backtest --symbol GBPUSD --timeframe H1
```

Backtest Report

The backtest generates:

· 📊 Performance Metrics - Win rate, Sharpe ratio, etc.
· 📈 Equity Curve - Visual representation of performance
· 📉 Drawdown Analysis - Maximum drawdown and duration
· 📊 Trade Distribution - Profit/loss distribution
· 📋 Monthly Returns - Performance by month

Output Files

```
reports/
├── report_GBPUSD_H1_20260101_143215.html    # HTML report
├── equity_curve_20260101_143215.png         # Equity curve chart
├── drawdown_20260101_143215.png             # Drawdown chart
└── trade_dist_20260101_143215.png           # Trade distribution
```

---

🛡️ Risk Management

Position Sizing

```python
# Calculate position size based on risk
volume = risk_amount / (stop_loss_pips * pip_value)
```

Stop Loss Rules

Rule Description
Minimum SL 20 pips
Maximum SL 200 pips
Breakeven SL Move to entry after +50 pips
Trailing SL Follow price with 30-pip trail

Daily Limits

Limit Description
Daily Loss Limit 10% of equity
Daily Risk Limit 5% of equity
Max Positions 5 concurrent

---

🐛 Troubleshooting

Common Issues

1. Connection Error: "MT5 not installed"

```bash
pip install MetaTrader5
```

2. Connection Error: "Login failed"

Check your MT5 credentials in config/settings.json

3. Dashboard not loading

```bash
# Check if dashboard server is running
ps aux | grep python

# Restart dashboard
python main.py --mode dashboard
```

4. No signals generated

```bash
# Check data feed
python main.py --mode analyze --symbol GBPUSD
```

5. Performance issues

```bash
# Reduce symbols or timeframe
# Check system resources
htop
```

---

❓ FAQ

Q: What is the minimum balance required?

A: $1,000 minimum recommended for live trading.

Q: How often are signals generated?

A: Every 5 seconds (configurable).

Q: Can I trade multiple symbols?

A: Yes, up to 10 symbols simultaneously.

Q: How accurate is the backtest?

A: Backtest accuracy depends on data quality and slippage assumptions.

Q: Is this suitable for beginners?

A: The dashboard is user-friendly, but trading knowledge is recommended.

Q: What's the success rate?

A: Target win rate is 65-75% with proper risk management.

---

📧 Support

For support, feature requests, or bug reports:

```
Seliim Ahmed
Email: amit.khanna.1082@gmail.com
GitHub: https://github.com/Khan-Amit
```

---

⚠️ Legal Disclaimer

IMPORTANT: Trading involves significant financial risk. Past performance does not guarantee future results. This trading engine is provided for educational and research purposes only. Users assume all responsibility for their trading decisions.

---

© 2026 Seliim Ahmed. All Rights Reserved.
MARDUK-TRADING-RIG™ · Part of the Marduk System™

"No Swift. No Middlemen. Just Probability."

```

---

**File 32 ready! Send me the next file name.** 📄
