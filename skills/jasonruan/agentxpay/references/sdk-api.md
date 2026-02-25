# AgentXPay SDK API 参考

## AgentXPayClient

主客户端类，整合所有模块。

### 构造函数

```typescript
new AgentXPayClient({
  rpcUrl: string,          // Monad RPC URL
  privateKey?: string,     // Agent 私钥
  signer?: ethers.Signer,  // 或传入 Signer 实例
  contracts?: {
    serviceRegistry?: string,
    paymentManager?: string,
    subscriptionManager?: string,
    escrow?: string,
    agentWalletFactory?: string,
  },
  network?: "local" | "testnet" | "mainnet",
})
```

### 核心方法

#### `client.fetch(url, options)` — x402 自动付费请求

```typescript
const response = await client.fetch("https://ai-service.com/api/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ prompt: "Hello" }),
  autoPayment: true,   // 自动处理 HTTP 402
  maxRetries: 1,        // 最大重试次数
});
```

#### `client.discoverServices(filter?)` — 服务发现

```typescript
const services = await client.discoverServices({
  category: "LLM",         // 可选：按类别过滤
  maxPrice: parseEther("0.05"), // 可选：最大单价
});
```

#### `client.subscribe(serviceId, planId, amount)` — 订阅

```typescript
const result = await client.subscribe(1n, 1n, parseEther("0.1"));
// { txHash, subscriptionId }
```

---

## 模块

### ServicesModule (`client.services`)

| 方法 | 说明 |
|------|------|
| `registerService(name, desc, endpoint, category, price)` | 注册服务 |
| `discoverServices(filter?)` | 发现服务 |
| `getServiceDetails(serviceId)` | 获取服务详情 |
| `getSubscriptionPlans(serviceId)` | 获取订阅计划 |
| `getServiceCount()` | 获取服务总数 |

### PaymentsModule (`client.payments`)

| 方法 | 说明 |
|------|------|
| `payPerUse(serviceId, amount)` | 按次付费 |
| `batchPay(serviceIds, totalAmount)` | 批量付费 |
| `deposit(amount)` | 预存余额 |
| `payFromBalance(serviceId)` | 从余额支付 |
| `withdraw(amount)` | 提取余额 |
| `getUserBalance(address)` | 查询用户余额 |
| `getProviderEarnings(address)` | 查询提供者收益 |

### SubscriptionsModule (`client.subscriptions`)

| 方法 | 说明 |
|------|------|
| `subscribe(serviceId, planId, amount)` | 订阅 |
| `cancelSubscription(subscriptionId)` | 取消订阅 |
| `renewSubscription(subscriptionId, amount)` | 续费 |
| `checkAccess(userAddress, serviceId)` | 检查访问权限 |
| `isActive(subscriptionId)` | 检查是否活跃 |

### EscrowModule (`client.escrow`)

| 方法 | 说明 |
|------|------|
| `createEscrow(serviceId, provider, deadline, desc, amount)` | 创建托管 |
| `releaseEscrow(escrowId)` | 释放资金 |
| `disputeEscrow(escrowId)` | 发起争议 |
| `refundEscrow(escrowId)` | 退款 |
| `getEscrow(escrowId)` | 查询托管 |

### WalletModule (`client.wallet`)

| 方法 | 说明 |
|------|------|
| `createWallet(dailyLimit)` | 创建 Agent 钱包 |
| `getWallets(owner)` | 查询用户钱包列表 |
| `getWalletInstance(address)` | 获取钱包实例 |

### AgentWalletClient

| 方法 | 说明 |
|------|------|
| `execute(to, value, data)` | 执行交易 |
| `setDailySpendingLimit(limit)` | 设置每日限额 |
| `authorizeAgent(agent)` | 授权操作者 |
| `revokeAgent(agent)` | 撤销授权 |
| `getDailySpendingLimit()` | 查询限额 |
| `getDailySpent()` | 查询今日已花费 |
| `getRemainingDailyAllowance()` | 查询剩余额度 |

---

## 合约地址

### Monad Testnet

- Chain ID: `10143`

- RPC: `https://testnet-rpc.monad.xyz/`

- 合约地址：

| 合约 | 地址 |
|------|------|
| ServiceRegistry | `0x5c932424AcBfab036969b3B9D94bA9eCbae7565D` |
| PaymentManager | `0x3949c97925e5Aa13e34ddb18EAbf0B70ABB0C7d4` |
| SubscriptionManager | `0x9e7F7d0E8b8F38e3CF2b3F7dd362ba2e9E82baa4` |
| Escrow | `0x0724F18B2aA7D6413D3fDcF6c0c27458a8170Dd9` |
| AgentWalletFactory | `0xE7FF84Df24A9a252B6E8A5BB093aC52B1d8bEEdf` |
