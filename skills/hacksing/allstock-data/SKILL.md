---
name: allstock-data
description: Query A-share and US stock data via Tencent Finance API. Use when user needs real-time or historical stock quotes, indices, ETF prices, or market data for Chinese or US markets.
---

# China Stock Data

Query A-share and US stock real-time market data.

## A-Share Data Query

### Base URL
```
http://qt.gtimg.cn/q=<stock_code>
```

### Stock Code Rules

| Market | Code Prefix | Example |
|--------|-------------|---------|
| Shanghai Main Board | sh600xxx | sh600560 |
| Shanghai STAR Market | sh688xxx | sh688xxx |
| Shenzhen Main Board | sz000xxx | sz000001 (Ping An Bank) |
| Shenzhen ChiNext | sz300xxx | sz300xxx |
| Shenzhen ETF | sz159xxx | sz159326 |

### Index Codes

| Index | Code |
|-------|------|
| Shanghai Composite | sh000001 |
| Shenzhen Component | sz399001 |
| ChiNext Index | sz399006 |
| STAR 50 | sz399987 |
| CSI 300 | sh000300 |

### Query Examples

**Single Stock:**
```
http://qt.gtimg.cn/q=sh600089
```

**Multiple Stocks (comma separated):**
```
http://qt.gtimg.cn/q=sh600089,sh600560,sz399001
```

### Return Data Format

Returns quasi-JSON format with fields separated by `~`:

```
v_sh600089="1~TEB~600089~28.75~28.92~28.63~1999256~...~-0.17~-0.59~..."
```

**Key Field Indices:**

| Index | Meaning |
|-------|---------|
| 0 | Market Code |
| 1 | Stock Name |
| 2 | Stock Code |
| 3 | Current Price |
| 4 | Open Price |
| 5 | Low Price |
| 6 | High Price |
| 30 | Change Amount |
| 31 | Change % |
| 32 | High Price |
| 33 | Low Price |

**Note**: The API returns change % field (index 31). Use this field instead of calculating it yourself.

## US Stock Data Query

Tencent Finance API has limited US stock support. Use these alternatives:

### Option 1: Yahoo Finance (Recommended)

```bash
curl -s "https://query1.finance.yahoo.com/v8/finance/chart/AAPL"
```

### Option 2: Alpha Vantage (Needs API Key)

```bash
curl -s "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey=YOUR_KEY"
```

### Common US Index Codes

| Index | Yahoo Code |
|-------|------------|
| Dow Jones | ^DJI |
| Nasdaq | ^IXIC |
| S&P 500 | ^GSPC |

## Data Parsing Examples

### Python - Parse Tencent Finance Data

```python
import re
import urllib.request

def get_stock_data(code):
    url = f"http://qt.gtimg.cn/q={code}"
    with urllib.request.urlopen(url) as response:
        data = response.read().decode('gbk')
    
    # Extract data
    match = re.search(r'="([^"]+)"', data)
    if not match:
        return None
    
    fields = match.group(1).split('~')
    
    return {
        'name': fields[1],
        'code': fields[2],
        'price': float(fields[3]),
        'open': float(fields[4]),
        'high': float(fields[5]),
        'low': float(fields[6]),
        'change': float(fields[30]),
        'change_pct': float(fields[31]),
    }

# Usage
data = get_stock_data('sh600089')
print(f"{data['name']}: {data['price']} ({data['change_pct']}%)")
```

### Using web_fetch Tool

```python
# Get multiple stock data
url = "http://qt.gtimg.cn/q=sh000001,sh600089,sz399001"
# Use web_fetch to get data, then parse
```

## Notes

1. **Encoding**: Tencent Finance returns GBK encoding, decode properly
2. **Change %**: Use API-returned field (index 31), avoid calculating manually
3. **Data Delay**: Real-time data may have 15-minute delay
4. **Request Frequency**: Avoid high-frequency requests, use batch queries
5. **Error Handling**: Invalid codes return `v_pv_none_match="1"`, check response content
