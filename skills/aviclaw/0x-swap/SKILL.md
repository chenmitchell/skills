# 0x Swap API Skill

⚠️ **SECURITY WARNING:** This skill involves real funds. Review all parameters before executing swaps.

## Install

```bash
cd skills/0x-swap
npm install
```

## Setup

```bash
# Get API key from https://dashboard.0x.org/
# Your key must have "Full Trading" access (not just prices)
export ZEROEX_API_KEY="your-api-key"

# Set your wallet private key (for signing swaps)
# Pass via PRIVATE_KEY environment variable
export PRIVATE_KEY="your-private-key-hex"
```

## API Key Requirements

⚠️ **IMPORTANT:** Your API key must have full trading access:
- Price-only keys return `transaction.to: null`
- Full trading keys return the full transaction object
- For gasless, enable "Gasless API" in your Dashboard app settings

## Usage

### Get Price Quote
```bash
node quote.js --sell USDC --buy WETH --amount 1 --chain base
```

### Execute Swap (AllowanceHolder)
```bash
node swap.js --sell USDC --buy WETH --amount 1 --chain base --wallet 0x...
```

### Execute Gasless Swap (Meta-transaction)
```bash
node gasless.js --sell USDC --buy WETH --amount 1 --chain base --wallet 0x...
```

## API Reference

### Endpoints

| Endpoint | Description |
|----------|-------------|
| `/swap/allowance-holder/quote` | Swap with on-chain approval |
| `/gasless/quote` | Gasless swap (meta-transaction) |
| `/gasless/submit` | Submit signed gasless swap |
| `/gasless/status/{tradeHash}` | Poll swap status |
| `/trade-analytics/swap` | Get completed swap trades |
| `/trade-analytics/gasless` | Get completed gasless trades |

### Required Headers (ALL requests)
```
0x-api-key: YOUR_API_KEY
0x-version: v2
```

### Required Parameters
- `sellToken`: Token address to sell
- `buyToken`: Token address to buy  
- `sellAmount`: Amount in base units (USDC = 6 decimals, WETH = 18 decimals)
- `chainId`: Chain ID (1=ETH, 8453=Base, etc.)
- `taker`: Wallet address executing the swap (REQUIRED)
- `slippagePercentage`: Max slippage (e.g., "1" for 1%) - RECOMMENDED

## Swap Types

### 1. AllowanceHolder (Most Reliable)

1. Get quote: `GET /swap/allowance-holder/quote`
2. Approve token to `quote.allowanceTarget`
3. Execute: `wallet.sendTransaction({ to: tx.to, data: tx.data })`

### 2. Gasless (Meta-transaction)

Requires: Enable "Gasless API" in Dashboard app settings

1. Get quote: `GET /gasless/quote`
2. Check `quote.approval` - if not null, sign the approval permit
3. Sign the trade: `wallet.signTypedData(quote.trade.eip712)`
4. Split signature to {v, r, s} format
5. Submit: `POST /gasless/submit`
6. Poll: `GET /gasless/status/{tradeHash}`

```javascript
// Sign trade
const tradeSig = hexToSignature(signature);
const submitBody = {
  trade: {
    type: quote.trade.type,  // "settler_metatransaction"
    eip712: quote.trade.eip712,
    signature: {
      v: Number(tradeSig.v),
      r: tradeSig.r,
      s: tradeSig.s,
      signatureType: 2
    }
  }
};

// Submit
const res = await fetch('https://api.0x.org/gasless/submit', {
  method: 'POST',
  headers: { '0x-api-key': API_KEY, '0x-version': 'v2', 'Content-Type': 'application/json' },
  body: JSON.stringify(submitBody)
});
const { tradeHash } = await res.json();
```

### 3. Permit2 (Advanced)

Similar to AllowanceHolder but uses EIP-712 permit for approval. More complex signature encoding.

## Trade History

### Get Swap Trades
```
GET https://api.0x.org/trade-analytics/swap?chainId=8453&taker=0x...
Headers: 0x-api-key: KEY, 0x-version: v2
```

### Get Gasless Trades
```
GET https://api.0x.org/trade-analytics/gasless?chainId=8453&taker=0x...
Headers: 0x-api-key: KEY, 0x-version: v2
```

Returns up to 200 trades. Use `nextCursor` for pagination.

## Supported Chains

| Chain | chainId |
|-------|---------|
| Ethereum | 1 |
| Base | 8453 |
| Polygon | 137 |
| Arbitrum | 42161 |
| Optimism | 10 |

## Token Addresses (Base)

| Token | Address |
|-------|---------|
| WETH | 0x4200000000000000000000000000000000000006 |
| USDC | 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 |
| DAI | 0x50c5725949A6F0C72E6C4a641F24049A917DB0Cb |

## Files

- `quote.js` - Get price quotes
- `swap.js` - Execute swap (AllowanceHolder)
- `gasless.js` - Execute gasless swap (meta-transaction)
- `package.json` - Dependencies

## Key Gotchas

- Quotes expire in ~30 seconds - refresh frequently
- Gasless requires enabling in Dashboard
- Cannot sell native ETH - wrap to WETH first
- Trade history may take time to index

## Security Best Practices

### 1. Private Key Management
- ⚠️ **NEVER** hardcode private keys in code or env vars
- Use encrypted keystores or HSM
- Consider using a hot/cold wallet setup (limited funds in hot wallet)

### 2. Slippage Protection
```javascript
// Always set slippage to protect against MEV/price impact
const quote = await fetch(`/swap/allowance-holder/quote?${new URLSearchParams({
  sellToken, buyToken, sellAmount,
  slippagePercentage: '1',  // 1% max slippage
  chainId: '8453'
})}`);

// Verify received amount meets minimum
const minBuyAmount = quote.buyAmount * 0.99;
```

### 3. Approval Security
```javascript
// ⚠️ NEVER approve unlimited amounts
// Approve only what you need

// Good: Exact amount
await token.approve(allowanceTarget, sellAmount);

// Bad: Unlimited (vulnerable to token contract hacks)
// await token.approve(allowanceTarget, ethers.MaxUint256);
```

### 4. Output Verification
```javascript
// Always verify swap output after execution
const balanceBefore = await token.balanceOf(wallet);
await wallet.sendTransaction({ to: tx.to, data: tx.data, value: tx.value });
const balanceAfter = await token.balanceOf(wallet);

const received = balanceAfter - balanceBefore;
if (received < minBuyAmount) {
  throw new Error('Swap failed: received less than minimum');
}
```

### 5. Gas Safety
```javascript
// Set reasonable gas limits to prevent overpayment
const gasLimit = Math.ceil(quote.gas * 1.2); // 20% buffer

await wallet.sendTransaction({
  to: tx.to,
  data: tx.data,
  gasLimit: gasLimit,
  maxFeePerGas: tx.maxFeePerGas,
  maxPriorityFeePerGas: tx.maxPriorityFeePerGas
});
```

### 6. Quote Expiration
- ⚠️ Quotes expire in ~30 seconds
- Execute immediately after getting quote
- Monitor for revert if quote expires

### 7. Token Allowances
- Check existing allowances before approving
- Revoke unused approvals to reduce attack surface
- Use Etherscan to verify approval targets
