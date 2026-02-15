# Setup

## Prerequisites

- Python 3.12+
- `requests` library (`pip install requests`)

## API Keys

You need one or both API keys:

1. **Site Manager API key** — for cloud access (works remotely)
   - Go to [unifi.ui.com](https://unifi.ui.com) → Account → API Keys → Create
   - This proxies requests through Ubiquiti's cloud to your console

2. **Local gateway API key** — for direct LAN access (faster, preferred when on-site)
   - Go to your console's local UI → Settings → API → Create
   - Requires the gateway IP (e.g. `192.168.0.2`)

The skill auto-detects which to use: local gateway when reachable, cloud connector when remote.

## Configuration

Create `config.json` next to SKILL.md (gitignored). Start from `config.json.example`.

```json
{
  "api_key": "YOUR_SITE_MANAGER_API_KEY",
  "gateway_ip": "192.168.0.2",
  "local_api_key": "YOUR_LOCAL_API_KEY"
}
```

| Field | Required | Description |
|---|---|---|
| `api_key` | Yes | Site Manager API key (cloud access) |
| `gateway_ip` | No | Local gateway/console IP address |
| `local_api_key` | No | Local gateway API key |
| `site_id` | No | Default site UUID (auto-detected if only one site) |

Alternatively, use environment variables: `UNIFI_API_KEY`, `UNIFI_GATEWAY_IP`, `UNIFI_LOCAL_API_KEY`.

## Cloud Connector Requirements

- Console firmware **≥ 5.0.3** (older firmware cannot be reached via cloud connector)
- Console must be registered and connected at [unifi.ui.com](https://unifi.ui.com)
