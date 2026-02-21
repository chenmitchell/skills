import axios from 'axios';

const API_KEY = 'e6eedf43-be5f-49e9-bb6c-8d9d5ce082d1';
const CHAINS = { base: 8453, ethereum: 1, polygon: 137, arbitrum: 42161, optimism: 10 };
const TOKENS = {
  8453: { WETH: '0x4200000000000000000000000000000000000006', USDC: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913' }
};

const chain = 'base';
const sellToken = 'USDC';
const buyToken = 'WETH';
const amount = '1'; // 1 USDC

const chainId = CHAINS[chain];
const sellAddr = TOKENS[chainId][sellToken];
const buyAddr = TOKENS[chainId][buyToken];
const sellAmount = (parseFloat(amount) * 1e6).toString(); // USDC decimals

const url = `https://api.0x.org/swap/permit2/quote?${new URLSearchParams({
  sellToken: sellAddr,
  buyToken: buyAddr,
  sellAmount,
  chainId: chainId.toString()
})}`;

console.log(`\n=== 0x Swap Quote (v2 API) ===`);
console.log(`Chain: ${chain} (${chainId})`);
console.log(`Sell: ${amount} ${sellToken}`);
console.log(`Buy: ${buyToken}\n`);

try {
  const response = await axios.get(url, { 
    headers: { '0x-api-key': API_KEY, '0x-version': 'v2' } 
  });
  
  const data = response.data;
  const price = Number(data.buyAmount) / Number(data.sellAmount) * 1e6;
  
  console.log(`✅ Quote received!`);
  console.log(`Price: 1 ${sellToken} = ${price.toFixed(6)} ${buyToken}`);
  console.log(`Buy amount: ${Number(data.buyAmount) / 1e18} ${buyToken}`);
  console.log(`Gas: ${data.gas} units`);
  console.log(`To: ${data.to}`);
  console.log(`\nPermit2: ${data.permit2 ? '✅ Gasless approval supported' : '❌ Not available'}`);
  
  if (data.issues?.balance?.actual === '0') {
    console.log(`\n⚠️ Warning: Insufficient balance!`);
  }
} catch (e) {
  console.error('Error:', e.response?.data || e.message);
}
