---
name: lifi
description: Use LI.FI API for cross-chain and same-chain swaps, bridges, and contract calls. Use when quoting routes, validating chains/tokens, building transaction requests, and tracking status.
homepage: https://docs.li.fi/
metadata:
  {
    "openclaw":
      {
        "emoji": "🔁",
        "requires": { "env": ["LIFI_API_KEY"], "bins": ["curl"] },
        "primaryEnv": "LIFI_API_KEY",
      },
  }
---

# LI.FI Agent Skill

## Purpose
Use the LI.FI API to fetch cross-chain and same-chain swap/bridge data, then
turn that data into a signed transaction that can be submitted by a wallet.

## Usage
use Endpoint Specifications to build transaction requests.
If the agent uses a native wallet like [openclast-wallet](https://github.com/fabriziogianni7/openclast-wallet/tree/master), use the `wallet_send` tool to send the transaction.


## Documentation
llm documentation: https://docs.li.fi/llms.txt
openapi spec: https://gist.githubusercontent.com/kenny-io/7fede47200a757195000bfbe14c5baee/raw/725cf9d4a6920d5b930925b0412d766aa53c701c/lifi-openapi.yaml

## Base URL and Auth
- Base URL: `https://li.quest`
- Auth: `x-lifi-api-key` header using `LIFI_API_KEY` when available; otherwise public access may be rate-limited.

## Config
- `LIFI_API_KEY` for higher rate limits and production usage.

## Required behavior (no web search)
- Do NOT use web search tools or require Brave/other search API keys.
- Fetch data directly from LI.FI endpoints (`https://li.quest`) using curl via shell commands (do not use fetch, axios, or other libraries—always execute curl for HTTP requests).
- Treat the OpenAPI spec as authoritative for endpoints, parameters, and headers (see spec in user prompt).
- NEVER use external price sources (Coinbase, etc.) to estimate quotes.
- If a quote is needed, call LI.FI `/v1/quote` or `/v1/advanced/routes` directly using curl.
- Do NOT ask for router/token addresses or slippage defaults if LI.FI responses can provide them.

## Wallet execution (Openclast wallet)
When the user asks to prepare or submit a transaction:
1. Fetch a LI.FI quote or route directly from LI.FI.
2. The wallet MUST use the returned `transactionRequest` object as the source
   of truth for the call (do not rebuild calldata).
3. Resolve the default wallet address:
   - Call `wallet_address` with no params to get `address` + `walletId`.
   - Use that `address` for `fromAddress` and `toAddress` in LI.FI requests.
4. Create a pending transaction with `wallet_contract_call` using:
   - `to` -> `wallet_contract_call.to`
   - `data` -> `wallet_contract_call.data`
   - `value` -> `wallet_contract_call.valueWei` (convert to wei string)
   - `gasLimit` -> `wallet_contract_call.gasLimit` (if present)
   - `gasPrice` -> `wallet_contract_call.gasPrice` (if present)
   - `maxFeePerGas` / `maxPriorityFeePerGas` -> matching fields (if present)
   - `nonce` -> `wallet_contract_call.nonce` (if present)
5. Ask for approval; if approved, submit the pending tx via `wallet_approve`.

## API Specification
> ## Documentation Index
> Fetch the complete documentation index at: https://docs.li.fi/llms.txt
> Use this file to discover all available pages before exploring further.

## Endpoint Specifications

Important: Execute via shell commands! Do not use fetch, axios, or other libraries—always execute curl for HTTP requests.

> Action-oriented reference for core LI.FI API endpoints

This page provides concise, action-oriented documentation for the core LI.FI API endpoints that AI agents need.

## Base URL

```
https://li.quest/v1
```

All endpoints use this base URL. Authentication via `x-lifi-api-key` header is optional but recommended for higher rate limits.

***

## GET /chains

**Action**: Retrieve all supported blockchain networks.

### Request

```bash  theme={"system"}
curl "https://li.quest/v1/chains"
```

### Parameters

| Parameter    | Type   | Required | Description                                                   |
| ------------ | ------ | -------- | ------------------------------------------------------------- |
| `chainTypes` | string | No       | Filter by type: `EVM`, `SVM`, `UTXO`, `MVM` (comma-separated) |

### Response

```json  theme={"system"}
{
  "chains": [
    {
      "id": 1,
      "key": "eth",
      "chainType": "EVM",
      "name": "Ethereum",
      "coin": "ETH",
      "mainnet": true,
      "logoURI": "https://raw.githubusercontent.com/lifinance/types/main/src/assets/icons/chains/ethereum.svg",
      "tokenlistUrl": "https://gateway.ipfs.io/ipns/tokens.uniswap.org",
      "multicallAddress": "0xcA11bde05977b3631167028862bE2a173976CA11",
      "metamask": {
        "chainId": "0x1",
        "blockExplorerUrls": ["https://etherscan.io/"],
        "chainName": "Ethereum Mainnet",
        "nativeCurrency": { "name": "ETH", "symbol": "ETH", "decimals": 18 },
        "rpcUrls": ["https://mainnet.infura.io/v3/"]
      },
      "nativeToken": {
        "address": "0x0000000000000000000000000000000000000000",
        "chainId": 1,
        "symbol": "ETH",
        "decimals": 18,
        "name": "ETH",
        "coinKey": "ETH",
        "logoURI": "https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/ethereum/assets/0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2/logo.png",
        "priceUSD": "2923.27"
      }
    }
    // ... 58 chains total
  ]
}
```

### Key Fields

| Field         | Use                                          |
| ------------- | -------------------------------------------- |
| `id`          | Chain ID for all other API calls             |
| `key`         | Short identifier (e.g., "eth", "arb", "pol") |
| `chainType`   | EVM, SVM (Solana), UTXO (Bitcoin), MVM (Sui) |
| `mainnet`     | true for production chains                   |
| `nativeToken` | Gas token with price                         |
| `metamask`    | Chain config for wallet connection           |

***

## GET /tokens

**Action**: Retrieve tokens available on specified chains.

### Request

```bash  theme={"system"}
curl "https://li.quest/v1/tokens?chains=1,42161"
```

### Parameters

| Parameter | Type   | Required | Description               |
| --------- | ------ | -------- | ------------------------- |
| `chains`  | string | Yes      | Comma-separated chain IDs |

### Response

```json  theme={"system"}
{
  "tokens": {
    "1": [
      {
        "address": "0x0000000000000000000000000000000000000000",
        "chainId": 1,
        "symbol": "ETH",
        "decimals": 18,
        "name": "ETH",
        "coinKey": "ETH",
        "logoURI": "https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/ethereum/assets/0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2/logo.png",
        "priceUSD": "2923.27"
      },
      {
        "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "chainId": 1,
        "symbol": "USDC",
        "decimals": 6,
        "name": "USD Coin",
        "coinKey": "USDC",
        "logoURI": "https://raw.githubusercontent.com/trustwallet/assets/master/blockchains/ethereum/assets/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48/logo.png",
        "priceUSD": "0.999606",
        "tags": ["stablecoin"]
      }
      // ... hundreds more tokens per chain
    ],
    "42161": [
      // ... tokens for Arbitrum
    ]
  }
}
```

### Key Fields

| Field      | Use                                            |
| ---------- | ---------------------------------------------- |
| `address`  | Token contract address (use in quote)          |
| `decimals` | For converting human amounts to smallest units |
| `priceUSD` | Current USD price                              |
| `coinKey`  | Canonical identifier across chains             |
| `tags`     | Categories like "stablecoin"                   |

### Native Token Address

Native tokens (ETH, MATIC, etc.) use: `0x0000000000000000000000000000000000000000`

***

## GET /quote

**Action**: Get a transfer quote with ready-to-execute transaction data.

### Request

```bash  theme={"system"}
curl "https://li.quest/v1/quote?fromChain=1&toChain=42161&fromToken=USDC&toToken=USDC&fromAmount=10000000&fromAddress=0x..."
```

### Parameters

| Parameter        | Type   | Required | Description                          |
| ---------------- | ------ | -------- | ------------------------------------ |
| `fromChain`      | number | **Yes**  | Source chain ID                      |
| `toChain`        | number | **Yes**  | Destination chain ID                 |
| `fromToken`      | string | **Yes**  | Source token address or symbol       |
| `toToken`        | string | **Yes**  | Destination token address or symbol  |
| `fromAmount`     | string | **Yes**  | Amount in smallest unit              |
| `fromAddress`    | string | **Yes**  | Sender wallet address                |
| `toAddress`      | string | No       | Recipient (defaults to fromAddress)  |
| `slippage`       | number | No       | Max slippage (default: 0.005 = 0.5%) |
| `order`          | string | No       | `FASTEST`, `CHEAPEST`                |
| `bridges`        | string | No       | Allowed bridges (comma-separated)    |
| `exchanges`      | string | No       | Allowed DEXs (comma-separated)       |
| `denyBridges`    | string | No       | Excluded bridges                     |
| `denyExchanges`  | string | No       | Excluded DEXs                        |
| `maxPriceImpact` | number | No       | Max price impact (e.g., 0.05 = 5%)   |

### Response

```json  theme={"system"}
{
  "type": "lifi",
  "id": "9f32864e-d704-46c1-874e-20f492c0ce77:0",
  "tool": "across",
  "toolDetails": {
    "key": "across",
    "name": "AcrossV4",
    "logoURI": "https://raw.githubusercontent.com/lifinance/types/main/src/assets/icons/bridges/across.svg"
  },
  "action": {
    "fromToken": {
      "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
      "chainId": 1,
      "symbol": "USDC",
      "decimals": 6,
      "name": "USD Coin",
      "coinKey": "USDC",
      "logoURI": "https://...",
      "priceUSD": "0.999606",
      "tags": ["stablecoin"]
    },
    "fromAmount": "10000000",
    "toToken": {
      "address": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
      "chainId": 42161,
      "symbol": "USDC",
      "decimals": 6,
      "name": "USD Coin",
      "coinKey": "USDC",
      "logoURI": "https://...",
      "priceUSD": "0.999606",
      "tags": ["stablecoin"]
    },
    "fromChainId": 1,
    "toChainId": 42161,
    "slippage": 0.001,
    "fromAddress": "0x552008c0f6870c2f77e5cC1d2eb9bdff03e30Ea0",
    "toAddress": "0x552008c0f6870c2f77e5cC1d2eb9bdff03e30Ea0"
  },
  "estimate": {
    "tool": "across",
    "approvalAddress": "0x1231DEB6f5749EF6cE6943a275A1D3E7486F4EaE",
    "toAmountMin": "9965731",
    "toAmount": "9965731",
    "fromAmount": "10000000",
    "feeCosts": [
      {
        "name": "LIFI Fixed Fee",
        "description": "Fixed LIFI fee, independent of any other fee",
        "token": { /* full token object */ },
        "amount": "25000",
        "amountUSD": "0.0250",
        "percentage": "0.0025",
        "included": true,
        "feeSplit": { "integratorFee": "0", "lifiFee": "25000" }
      }
      // ... additional fee items
    ],
    "gasCosts": [
      {
        "type": "SEND",
        "price": "65729222",
        "estimate": "220266",
        "limit": "286346",
        "amount": "14477912813052",
        "amountUSD": "0.0423",
        "token": { /* native token object */ }
      }
    ],
    "executionDuration": 4,
    "fromAmountUSD": "9.9961",
    "toAmountUSD": "9.9618"
  },
  "includedSteps": [
    {
      "id": "e1c87be5-80be-4e2d-8c96-a6492566a739",
      "type": "protocol",
      "action": { /* step action */ },
      "estimate": { /* step estimate */ },
      "tool": "feeCollection",
      "toolDetails": { /* tool info */ }
    },
    {
      "id": "529839e7-a048-4abe-99ad-d650a0fe469e",
      "type": "cross",
      "action": { /* step action */ },
      "estimate": { /* step estimate */ },
      "tool": "across",
      "toolDetails": { /* tool info */ }
    }
  ],
  "integrator": "lifi-api",
  "transactionRequest": {
    "value": "0x0",
    "to": "0x1231DEB6f5749EF6cE6943a275A1D3E7486F4EaE",
    "data": "0x1794958f...",
    "from": "0x552008c0f6870c2f77e5cC1d2eb9bdff03e30Ea0",
    "chainId": 1,
    "gasPrice": "0x3eaf2c6",
    "gasLimit": "0x45e8a"
  },
  "transactionId": "0x1695bded7c1634dce4a200bdec72be0ed6cc5f7153ec2dc832b271d790eb00c8"
}
```

<Note>
  See the [Five-Call Recipe](/agents/quick-start/five-call-recipe#call-3-get-a-quote) for the complete untruncated response.
</Note>

### Key Fields

| Field                      | Use                                                             |
| -------------------------- | --------------------------------------------------------------- |
| `tool`                     | Bridge/DEX used (optional for status check, speeds up response) |
| `estimate.toAmount`        | Expected output amount                                          |
| `estimate.toAmountMin`     | Minimum guaranteed (slippage-protected)                         |
| `estimate.approvalAddress` | Spender address for ERC20 approval                              |
| `estimate.feeCosts`        | Detailed fee breakdown                                          |
| `estimate.gasCosts`        | Gas cost estimates                                              |
| `includedSteps`            | Each step in multi-step transfers                               |
| `transactionRequest`       | Ready-to-sign transaction object                                |
| `transactionId`            | Unique ID for tracking                                          |

### Constraints

* `fromAmount` must be in smallest unit (e.g., 6 decimals for USDC)
* `slippage` is a decimal (0.005 = 0.5%, not 0.5)
* Quote expires after \~60 seconds

***

## GET /status

**Action**: Check the status of a cross-chain transfer.

### Request

```bash  theme={"system"}
curl "https://li.quest/v1/status?txHash=0x..."
```

### Parameters

| Parameter   | Type   | Required | Description                             |
| ----------- | ------ | -------- | --------------------------------------- |
| `txHash`    | string | **Yes**  | Source chain transaction hash           |
| `fromChain` | number | No       | Source chain ID (recommended for speed) |
| `toChain`   | number | No       | Destination chain ID                    |
| `bridge`    | string | No       | Bridge tool from quote                  |

<Note>
  Only `txHash` is required. Providing `fromChain` significantly speeds up the response.
</Note>

### Response

```json  theme={"system"}
{
  "transactionId": "0x1695bded7c1634dce4a200bdec72be0ed6cc5f7153ec2dc832b271d790eb00c8",
  "sending": {
    "txHash": "0x1695bded7c1634dce4a200bdec72be0ed6cc5f7153ec2dc832b271d790eb00c8",
    "txLink": "https://etherscan.io/tx/0x1695bded7c1634dce4a200bdec72be0ed6cc5f7153ec2dc832b271d790eb00c8",
    "chainId": 1,
    "amount": "10000000",
    "token": {
      "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
      "chainId": 1,
      "symbol": "USDC",
      "decimals": 6,
      "name": "USD Coin",
      "coinKey": "USDC",
      "logoURI": "https://...",
      "priceUSD": "0.999606"
    },
    "amountUSD": "9.9961",
    "gasPrice": "65729222",
    "gasUsed": "220266",
    "gasToken": { /* native token */ },
    "gasAmount": "14477912813052",
    "gasAmountUSD": "0.0423",
    "timestamp": 1737625200
  },
  "receiving": {
    "txHash": "0xdef456789abc...",
    "txLink": "https://arbiscan.io/tx/0xdef456789abc...",
    "chainId": 42161,
    "amount": "9965731",
    "token": {
      "address": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
      "chainId": 42161,
      "symbol": "USDC",
      "decimals": 6,
      "name": "USD Coin",
      "coinKey": "USDC",
      "logoURI": "https://...",
      "priceUSD": "0.999606"
    },
    "amountUSD": "9.9618",
    "timestamp": 1737625204
  },
  "lifiExplorerLink": "https://explorer.li.fi/tx/0x1695bded7c1634dce4a200bdec72be0ed6cc5f7153ec2dc832b271d790eb00c8",
  "fromAddress": "0x552008c0f6870c2f77e5cC1d2eb9bdff03e30Ea0",
  "toAddress": "0x552008c0f6870c2f77e5cC1d2eb9bdff03e30Ea0",
  "tool": "across",
  "status": "DONE",
  "substatus": "COMPLETED"
}
```

### Key Fields

| Field              | Use                           |
| ------------------ | ----------------------------- |
| `status`           | Main status (see table below) |
| `substatus`        | Detailed outcome              |
| `sending.txHash`   | Source chain transaction      |
| `receiving.txHash` | Destination chain transaction |
| `lifiExplorerLink` | Link to LI.FI explorer        |
| `receiving.amount` | Actual received amount        |

### Status Values

| Status      | Substatus   | Meaning                            |
| ----------- | ----------- | ---------------------------------- |
| `NOT_FOUND` | -           | Transaction not indexed yet        |
| `PENDING`   | -           | Transfer in progress               |
| `DONE`      | `COMPLETED` | Success - received requested token |
| `DONE`      | `PARTIAL`   | Success - received different token |
| `DONE`      | `REFUNDED`  | Failed - tokens returned to sender |
| `FAILED`    | various     | Permanent failure (see substatus)  |

***

## POST /advanced/routes

**Action**: Get multiple route options for a transfer.

### Request

```bash  theme={"system"}
curl -X POST "https://li.quest/v1/advanced/routes" \
  -H "Content-Type: application/json" \
  -d '{
    "fromChainId": 1,
    "toChainId": 42161,
    "fromTokenAddress": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "toTokenAddress": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
    "fromAmount": "10000000",
    "fromAddress": "0x..."
  }'
```

### Parameters (JSON Body)

| Parameter          | Type   | Required | Description               |
| ------------------ | ------ | -------- | ------------------------- |
| `fromChainId`      | number | **Yes**  | Source chain ID           |
| `toChainId`        | number | **Yes**  | Destination chain ID      |
| `fromTokenAddress` | string | **Yes**  | Source token address      |
| `toTokenAddress`   | string | **Yes**  | Destination token address |
| `fromAmount`       | string | **Yes**  | Amount in smallest unit   |
| `fromAddress`      | string | **Yes**  | Sender address            |
| `options`          | object | No       | Additional options        |

### Response

```json  theme={"system"}
{
  "routes": [
    {
      "id": "0x...",
      "steps": [...],
      "toAmount": "9900000",
      "toAmountMin": "9850000",
      "gasCostUSD": "5.23",
      "tags": []
    }
  ]
}
```

### When to Use

* Need multiple route options
* User wants to compare bridges
* Complex multi-hop transfers

***

## POST /advanced/stepTransaction

**Action**: Get transaction data for a specific route step.

### Request

```bash  theme={"system"}
curl -X POST "https://li.quest/v1/advanced/stepTransaction" \
  -H "Content-Type: application/json" \
  -d '{ "step": { ... } }'
```

### Parameters

| Parameter | Type   | Required | Description                      |
| --------- | ------ | -------- | -------------------------------- |
| `step`    | object | **Yes**  | Step object from routes response |

### Response

Returns the step with `transactionRequest` populated.

### When to Use

After `/advanced/routes` to get transaction data for each step.

***

## GET /connections

**Action**: Get all possible token connections from/to a chain.

### Request

```bash  theme={"system"}
curl "https://li.quest/v1/connections?fromChain=1&toChain=42161"
```

### Parameters

| Parameter   | Type   | Required | Description                 |
| ----------- | ------ | -------- | --------------------------- |
| `fromChain` | number | No\*     | Source chain ID             |
| `toChain`   | number | No\*     | Destination chain ID        |
| `fromToken` | string | No       | Filter by source token      |
| `toToken`   | string | No       | Filter by destination token |

\*At least one of `fromChain` or `toChain` required.

### Response

```json  theme={"system"}
{
  "connections": [
    {
      "fromChainId": 1,
      "toChainId": 42161,
      "fromTokens": [
        {
          "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
          "chainId": 1,
          "symbol": "USDC",
          "decimals": 6,
          "name": "USD Coin",
          "coinKey": "USDC",
          "logoURI": "https://...",
          "priceUSD": "0.999606"
        }
        // ... more tokens that can be sent
      ],
      "toTokens": [
        {
          "address": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
          "chainId": 42161,
          "symbol": "USDC",
          "decimals": 6,
          "name": "USD Coin",
          "coinKey": "USDC",
          "logoURI": "https://...",
          "priceUSD": "0.999606"
        }
        // ... more tokens that can be received
      ]
    }
  ]
}
```

### Key Fields

| Field         | Use                         |
| ------------- | --------------------------- |
| `fromChainId` | Source chain                |
| `toChainId`   | Destination chain           |
| `fromTokens`  | Tokens that can be sent     |
| `toTokens`    | Tokens that can be received |

### When to Use

* Check if a route is possible before quoting
* Discover available destination tokens
* Build token selection UI

***

## GET /tools

**Action**: Get available bridges and exchanges.

### Request

```bash  theme={"system"}
curl "https://li.quest/v1/tools"
```

### Response

```json  theme={"system"}
{
  "bridges": [
    {
      "key": "across",
      "name": "AcrossV4",
      "logoURI": "https://raw.githubusercontent.com/lifinance/types/main/src/assets/icons/bridges/across.svg",
      "supportedChains": [
        { "fromChainId": 1, "toChainId": 42161 },
        { "fromChainId": 1, "toChainId": 10 },
        { "fromChainId": 1, "toChainId": 137 }
        // ... more chain pairs
      ]
    },
    {
      "key": "stargate",
      "name": "Stargate",
      "logoURI": "https://raw.githubusercontent.com/lifinance/types/main/src/assets/icons/bridges/stargate.png",
      "supportedChains": [
        { "fromChainId": 1, "toChainId": 42161 },
        { "fromChainId": 1, "toChainId": 43114 }
        // ... more chain pairs
      ]
    }
    // ... 27 bridges total
  ],
  "exchanges": [
    {
      "key": "uniswap",
      "name": "Uniswap V3",
      "logoURI": "https://raw.githubusercontent.com/lifinance/types/main/src/assets/icons/exchanges/uniswap.png",
      "supportedChains": [1, 42161, 10, 137, 8453]
    },
    {
      "key": "1inch",
      "name": "1inch",
      "logoURI": "https://raw.githubusercontent.com/lifinance/types/main/src/assets/icons/exchanges/oneinch.png",
      "supportedChains": [1, 42161, 10, 137, 8453, 43114]
    }
    // ... 31 exchanges total
  ]
}
```

### Key Fields

| Field                         | Use                                       |
| ----------------------------- | ----------------------------------------- |
| `bridges[].key`               | Use in `allowBridges` / `denyBridges`     |
| `bridges[].supportedChains`   | Check if bridge supports your chain pair  |
| `exchanges[].key`             | Use in `allowExchanges` / `denyExchanges` |
| `exchanges[].supportedChains` | Chains where DEX is available             |

### When to Use

* Filter routes by specific bridges/exchanges
* Show available tools to users
* Validate bridge/exchange selection

***

## Quick Reference

| Endpoint                    | Method | Purpose                    |
| --------------------------- | ------ | -------------------------- |
| `/chains`                   | GET    | List supported chains      |
| `/tokens`                   | GET    | Get tokens for chains      |
| `/quote`                    | GET    | Get quote with tx data     |
| `/status`                   | GET    | Check transfer status      |
| `/advanced/routes`          | POST   | Get multiple route options |
| `/advanced/stepTransaction` | POST   | Get tx data for route step |
| `/connections`              | GET    | Check route availability   |
| `/tools`                    | GET    | List bridges and exchanges |

***

## Related Pages

* [Five-Call Recipe](/agents/quick-start/five-call-recipe) - Complete workflow
* [Schemas](/agents/reference/schemas) - Detailed type definitions
* [Error Playbooks](/agents/reference/error-playbooks) - Error handling

