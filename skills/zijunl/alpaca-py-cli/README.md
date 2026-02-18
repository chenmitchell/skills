# Alpaca Trading (Python CLI)

[![ClawHub](https://img.shields.io/badge/ClawHub-alpaca--py--cli-blue)](https://clawhub.ai/skills/alpaca-py-cli)
[![GitHub](https://img.shields.io/badge/GitHub-zijunl%2Falpaca--py--cli-green)](https://github.com/zijunl/alpaca-py-cli)
[![Version](https://img.shields.io/badge/version-1.1.0-orange)](https://clawhub.ai/skills/alpaca-py-cli)

A Python-based command-line interface for trading stocks and crypto via Alpaca Markets API.

## 🚀 Quick Install

### Via ClawHub (Recommended)

```bash
npm install -g clawhub
clawhub install alpaca-py-cli
```

### Manual Install

```bash
git clone https://github.com/zijunl/alpaca-py-cli.git
cd alpaca-py-cli
brew install python@3.11
/opt/homebrew/bin/pip3.11 install alpaca-py pytz
```

## ✨ Features

- 📈 Real-time stock quotes
- 💼 Portfolio management
- 📊 Account information
- 🔄 Order execution (market orders)
- 📅 Market calendar
- 📉 Portfolio history
- ⏰ Market status checking
- 🔐 Secure credential management
- 📝 Paper trading support

## 🎯 Quick Start

1. Install dependencies:
   ```bash
   brew install python@3.11
   /opt/homebrew/bin/pip3.11 install alpaca-py pytz
   ```

2. Configure API keys:
   ```bash
   alpaca auth
   ```

3. Test it out:
   ```bash
   alpaca clock
   alpaca account
   alpaca quote AAPL
   ```

## 📚 Commands

```bash
alpaca auth          # Configure API keys
alpaca clock         # Market status
alpaca calendar      # Trading calendar
alpaca history       # Portfolio history
alpaca account       # Account information
alpaca quote AAPL    # Stock quotes
alpaca positions     # Current holdings
alpaca orders        # Order management
alpaca buy/sell      # Execute trades
alpaca cancel/close  # Cancel/close positions
```

## 🔗 Links

- **ClawHub**: https://clawhub.ai/skills/alpaca-py-cli
- **GitHub**: https://github.com/zijunl/alpaca-py-cli
- **Alpaca Markets**: https://alpaca.markets
- **Python SDK Docs**: https://alpaca.markets/docs/python-sdk/

## 🛡️ Why This Skill?

This is a lightweight Python implementation of the Alpaca Trading CLI, designed to be:

- **Easy to install**: Just Python + pip packages
- **Cross-platform**: Works on macOS, Linux, Windows
- **Well-documented**: Clear examples and troubleshooting
- **Safe**: Emphasizes paper trading and credential security
- **Agent-friendly**: Designed for OpenClaw agent automation

## 🆚 Differences from Other Alpaca Skills

- **alpaca-trading** (ClawHub): Uses `apcacli` (Rust CLI, third-party tool)
- **alpaca** (ClawHub): Uses Python scripts but different implementation
- **alpaca-py-cli** (this skill): Custom Python CLI with Homebrew Python support

## 🔒 Safety & Security

- Always test with paper trading first
- API keys stored in shell config (not in code)
- Interactive `alpaca auth` hides secret key input
- Market orders only (no complex order types to reduce risk)
- Confirmation required for `close-all` command

## 📖 Documentation

Full documentation available in [SKILL.md](SKILL.md)

## 🤝 Contributing

Contributions welcome! Please open an issue or PR on GitHub.

## 📄 License

MIT License - Free to use, modify, and distribute

## 👤 Author

Created for the OpenClaw community by [@zijunl](https://github.com/zijunl)

## 💬 Support

- GitHub Issues: https://github.com/zijunl/alpaca-py-cli/issues
- OpenClaw Discord: https://discord.com/invite/clawd
- ClawHub: https://clawhub.ai/skills/alpaca-py-cli
