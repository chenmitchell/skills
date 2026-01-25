---
name: nest-devices
description: Control Nest smart home devices (thermostat, cameras, doorbell) via the Device Access API. Use when asked to check or adjust home temperature, view camera feeds, check who's at the door, monitor rooms, or set up temperature schedules.
metadata:
  clawdbot:
    emoji: "🏠"
---

# Nest Device Access

Control Nest devices via Google's Smart Device Management API.

## Setup

### 1. Google Cloud & Device Access

1. Create a Google Cloud project at [console.cloud.google.com](https://console.cloud.google.com)
2. Pay the $5 fee and create a Device Access project at [console.nest.google.com/device-access](https://console.nest.google.com/device-access)
3. Create OAuth 2.0 credentials (Web application type)
4. Add `https://www.google.com` as an authorized redirect URI
5. Link your Nest account to the Device Access project

### 2. Get Refresh Token

Run the OAuth flow to get a refresh token:

```bash
# 1. Open this URL in browser (replace CLIENT_ID and PROJECT_ID):
https://nestservices.google.com/partnerconnections/PROJECT_ID/auth?redirect_uri=https://www.google.com&access_type=offline&prompt=consent&client_id=CLIENT_ID&response_type=code&scope=https://www.googleapis.com/auth/sdm.service

# 2. Authorize and copy the 'code' parameter from the redirect URL

# 3. Exchange code for tokens:
curl -X POST https://oauth2.googleapis.com/token \
  -d "client_id=CLIENT_ID" \
  -d "client_secret=CLIENT_SECRET" \
  -d "code=AUTH_CODE" \
  -d "grant_type=authorization_code" \
  -d "redirect_uri=https://www.google.com"
```

### 3. Store Credentials

Store in 1Password or environment variables:

**1Password** (recommended):
Create an item with fields: `project_id`, `client_id`, `client_secret`, `refresh_token`

**Environment variables:**
```bash
export NEST_PROJECT_ID="your-project-id"
export NEST_CLIENT_ID="your-client-id"
export NEST_CLIENT_SECRET="your-client-secret"
export NEST_REFRESH_TOKEN="your-refresh-token"
```

## Usage

### List devices
```bash
python3 scripts/nest.py list
```

### Thermostat

```bash
# Get status
python3 scripts/nest.py get <device_id>

# Set temperature (Celsius)
python3 scripts/nest.py set-temp <device_id> 21 --unit c --type heat

# Set temperature (Fahrenheit)
python3 scripts/nest.py set-temp <device_id> 70 --unit f --type heat

# Change mode (HEAT, COOL, HEATCOOL, OFF)
python3 scripts/nest.py set-mode <device_id> HEAT

# Eco mode
python3 scripts/nest.py set-eco <device_id> MANUAL_ECO
```

### Cameras

```bash
# Generate live stream URL (RTSP, valid ~5 min)
python3 scripts/nest.py stream <device_id>
```

## Python API

```python
from nest import NestClient

client = NestClient()

# List devices
devices = client.list_devices()

# Thermostat control
client.set_heat_temperature(device_id, 21.0)  # Celsius
client.set_thermostat_mode(device_id, 'HEAT')
client.set_eco_mode(device_id, 'MANUAL_ECO')

# Camera stream
result = client.generate_stream(device_id)
rtsp_url = result['results']['streamUrls']['rtspUrl']
```

## Configuration

The script checks for credentials in this order:

1. **1Password**: Set `NEST_OP_VAULT` and `NEST_OP_ITEM` (or use defaults: vault "Alfred", item "Nest Device Access API")
2. **Environment variables**: `NEST_PROJECT_ID`, `NEST_CLIENT_ID`, `NEST_CLIENT_SECRET`, `NEST_REFRESH_TOKEN`

## Temperature Reference

| Setting | Celsius | Fahrenheit |
|---------|---------|------------|
| Eco (away) | 15-17°C | 59-63°F |
| Comfortable | 19-21°C | 66-70°F |
| Warm | 22-23°C | 72-73°F |
| Night | 17-18°C | 63-65°F |

## Limitations

- Camera streams expire after ~5 minutes
- Real-time events (doorbell, motion) require Google Cloud Pub/Sub subscription
- Some older Nest devices may not support all features
