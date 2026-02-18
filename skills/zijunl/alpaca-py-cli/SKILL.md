---
name: alpaca-py-cli
description: Trade stocks and crypto via Alpaca API using Python CLI. Use for market data (quotes, bars, news), placing orders (market, limit, stop), checking positions, portfolio management, and account info. Supports both paper and live trading. Use when user asks about stock prices, wants to buy/sell securities, check portfolio, or manage trades.
metadata: {"clawdbot":{"emoji":"📈","requires":{"bins":["python3"],"packages":["alpaca-py","pytz"]},"install":[{"id":"pip-alpaca","kind":"pip","package":"alpaca-py","label":"Install alpaca-py (pip3 install alpaca-py)"},{"id":"pip-pytz","kind":"pip","package":"pytz","label":"Install pytz (pip3 install pytz)"}],"setup":{"instructions":["Get API keys from https://alpaca.markets","Run: alpaca auth (interactive setup)","Test: alpaca clock"]}}}
homepage: https://github.com/zijunl/alpaca-py-cli
---

# Alpaca Trading (Python CLI)

[![ClawHub](https://img.shields.io/badge/ClawHub-alpaca--py--cli-blue)](https://clawhub.ai/skills/alpaca-py-cli)
[![GitHub](https://img.shields.io/badge/GitHub-zijunl%2Falpaca--py--cli-green)](https://github.com/zijunl/alpaca-py-cli)

Trade stocks and crypto programmatically via Alpaca's API using a Python-based CLI tool.

**Links:**
- ClawHub: https://clawhub.ai/skills/alpaca-py-cli
- GitHub: https://github.com/zijunl/alpaca-py-cli
- Alpaca Markets: https://alpaca.markets

## Overview

Manage your Alpaca Markets trading account using the `alpaca` CLI tool and Python SDK. Supports both paper trading (simulated) and live trading.

## Installation

### Recommended: Homebrew Python (avoids urllib3/LibreSSL warnings)

```bash
# Install Homebrew Python 3.11+
brew install python@3.11

# Install alpaca-py
/opt/homebrew/bin/pip3.11 install alpaca-py pytz
```

### Alternative: System Python

```bash
pip3 install alpaca-py pytz
```

**Note:** System Python may show urllib3 warnings on macOS due to LibreSSL compatibility. Use Homebrew Python for a cleaner experience.

## Configuration

### Quick Setup with CLI

```bash
alpaca auth
```

This will interactively prompt you for:
- API Key
- Secret Key (hidden input)
- Trading mode (Paper or Live)

The command automatically saves your credentials to your shell config file (`~/.zshrc`, `~/.bashrc`, or `~/.profile`).

### Manual Setup

Alternatively, set these in your shell profile manually:

```bash
export ALPACA_API_KEY="your_api_key"
export ALPACA_SECRET_KEY="your_secret_key"
export ALPACA_PAPER="true"  # Use "false" for live trading
```

Get your API keys from https://alpaca.markets (Dashboard → API Keys)

**Paper Trading** (recommended for testing):
- Use paper trading API keys
- Virtual $100,000 starting balance
- No real money at risk

**Live Trading** (real money):
- Use live trading API keys
- Real money, real risk
- Test thoroughly with paper trading first

## CLI Commands

### Setup & Configuration

#### Configure Credentials

```bash
alpaca auth
```

Interactive setup wizard that guides you through:
1. Enter API Key
2. Enter Secret Key (hidden)
3. Choose trading mode (Paper/Live)
4. Automatically saves to shell config

### Account & Market Info

#### Check Account

```bash
alpaca account
```

Shows:
- Account number and status
- Portfolio value, cash, buying power
- P&L (equity, last equity)
- Trading restrictions (pattern day trader, blocks)

#### Check Market Status

```bash
alpaca clock
```

Shows:
- Market status (🟢 OPEN or 🔴 CLOSED)
- Current time
- Next open/close times

#### View Market Calendar

```bash
# Show next 30 trading days (default)
alpaca calendar

# Show next 7 trading days
alpaca calendar --days 7
```

Shows trading days with open/close times (Eastern Time).

#### View Portfolio History

```bash
# Default: 1 month, daily bars
alpaca history

# Last week
alpaca history --period 1W

# Last 3 months with hourly bars
alpaca history --period 3M --timeframe 1H
```

**Periods:** 1D, 1W, 1M, 3M, 1Y, all  
**Timeframes:** 1Min, 5Min, 15Min, 1H, 1D

Shows:
- Start and end equity
- Total change ($ and %)
- Recent history (last 10 data points)

### Portfolio Management

#### View Positions

```bash
alpaca positions
```

Shows all current holdings with:
- Symbol, quantity, current price
- Entry price and market value
- Unrealized P&L ($ and %)
- Total portfolio value and P&L

#### Get Stock Quotes

```bash
# Single symbol
alpaca quote AAPL

# Multiple symbols
alpaca quote AAPL,TSLA,MSFT
```

Shows:
- Bid and ask prices
- Mid price and spread
- Quote timestamp

**Note:** Quotes may show incomplete data when market is closed. Best used during market hours (9:30 AM - 4:00 PM ET).

### Order Management

#### View Orders

```bash
# Show open orders (default)
alpaca orders

# Show all recent orders
alpaca orders --status all

# Show last 20 closed orders
alpaca orders --status closed --limit 20
```

Shows:
- Order status with emoji indicators (⏳ pending, ✓ filled, ✗ canceled)
- Symbol, side (BUY/SELL), quantity
- Order ID and creation time
- Fill price (if filled)

#### Place Orders

```bash
# Buy shares
alpaca buy AAPL 10

# Sell shares
alpaca sell AAPL 5
```

Places a market order that executes at market price when market is open.

#### Cancel Orders

```bash
# Cancel specific order
alpaca cancel <order_id>

# Cancel all open orders
alpaca cancel-all
```

### Position Management

#### Close Positions

```bash
# Close specific position
alpaca close AAPL

# Close all positions (requires confirmation)
alpaca close-all
```

**Note:** `close-all` will prompt for confirmation before closing all positions.

## Example Workflows

### First Time Setup

```bash
# Configure credentials
alpaca auth

# Check account
alpaca account

# Check if market is open
alpaca clock
```

### Trading Workflow

```bash
# Check current price
alpaca quote TSLA

# Check account balance
alpaca account

# Buy some shares
alpaca buy TSLA 5

# Check pending orders
alpaca orders

# View positions (after order fills)
alpaca positions

# Get updated quote
alpaca quote TSLA

# Sell some shares
alpaca sell TSLA 2

# Check order history
alpaca orders --status all
```

### Portfolio Analysis

```bash
# View current positions
alpaca positions

# View portfolio history
alpaca history --period 1M

# Check market calendar
alpaca calendar --days 7
```

### Risk Management

```bash
# Check all open orders
alpaca orders

# Cancel specific order
alpaca cancel <order_id>

# Cancel all orders
alpaca cancel-all

# Close specific position
alpaca close AAPL

# Close all positions
alpaca close-all
```

## Agent Usage

When the user asks about their portfolio or wants to trade:

1. **Configure credentials**: Run `alpaca auth` for first-time setup
2. **Check market status**: Run `alpaca clock` to see if market is open
3. **Check account**: Run `alpaca account` to see current balance and buying power
4. **Get positions**: Run `alpaca positions` to list current holdings
5. **View orders**: Run `alpaca orders` to see pending/recent orders
6. **Get quotes**: Run `alpaca quote <symbols>` to check current prices
7. **Place orders**: Run `alpaca buy/sell` to execute trades
8. **Manage risk**: Run `alpaca cancel/close` commands as needed

## Safety Tips

- **Always test with paper trading first** (`ALPACA_PAPER=true`)
- Use `alpaca auth` to safely configure credentials (secret key is hidden)
- Check `alpaca clock` before trading to see if market is open
- Check quotes before placing orders to understand current prices
- Check `account.buying_power` before placing orders
- Use `TimeInForce.DAY` to auto-cancel unfilled orders at market close
- Monitor positions regularly with `alpaca positions`
- Check order status with `alpaca orders`
- Review portfolio performance with `alpaca history`
- Use `alpaca cancel-all` to quickly cancel all pending orders
- Use `alpaca close-all` with caution (requires confirmation)
- Set stop-loss orders for risk management
- Never share your API keys publicly

## Market Hours

US stock market hours (Eastern Time):
- **Regular hours**: 9:30 AM - 4:00 PM ET
- **Pre-market**: 4:00 AM - 9:30 AM ET
- **After-hours**: 4:00 PM - 8:00 PM ET

Orders placed outside market hours will be queued and executed when market opens.

Quotes may show incomplete or stale data when market is closed.

Use `alpaca clock` to check current market status.

## Troubleshooting

### urllib3 Warning (LibreSSL)

If you see:
```
NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently using LibreSSL
```

**Solution:** Install and use Homebrew Python 3.11+ which uses OpenSSL:
```bash
brew install python@3.11
/opt/homebrew/bin/pip3.11 install alpaca-py pytz
```

Then update the script shebang to use Homebrew Python:
```bash
sed -i '' '1s|#!/usr/bin/env python3|#!/opt/homebrew/bin/python3.11|' ~/.openclaw/workspace/skills/alpaca-py-cli/scripts/alpaca
```

### Missing pytz

If you see:
```
ModuleNotFoundError: No module named 'pytz'
```

**Solution:**
```bash
pip3 install pytz
# or
/opt/homebrew/bin/pip3.11 install pytz
```

### Command Not Found

If `alpaca` command is not found, use the full path:
```bash
~/.openclaw/workspace/skills/alpaca-py-cli/scripts/alpaca
```

Or add to PATH in your shell config:
```bash
export PATH="$HOME/.openclaw/workspace/skills/alpaca-py-cli/scripts:$PATH"
```

## Files

- **CLI Tool**: `~/.openclaw/workspace/skills/alpaca-py-cli/scripts/alpaca`
- **Config**: Environment variables in `~/.zshrc` (or `~/.bashrc`, `~/.profile`)

## Official Documentation

- Python SDK: https://alpaca.markets/docs/python-sdk/
- API Reference: https://docs.alpaca.markets/reference/
- Trading API: https://docs.alpaca.markets/docs/trading-api
- Market Data API: https://docs.alpaca.markets/docs/market-data
