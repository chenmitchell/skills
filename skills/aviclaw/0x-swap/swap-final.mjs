import { ethers } from 'ethers';

const PRIVATE_KEY = process.env.X402_KEY;
const API_KEY = 'e6eedf43-be5f-49e9-bb6c-8d9d5ce082d1';
const WALLET = '0x6581ff3C7D8dB9cFd7f8d34e0901d1151DAeC11E';

const provider = new ethers.JsonRpcProvider('https://mainnet.base.org');
const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

console.log('=== Proper 0x Swap ===');
console.log('Wallet:', wallet.address);

// Get quote with transaction data
const quoteUrl = `https://api.0x.org/swap/allowance-holder/quote?${new URLSearchParams({
  sellToken: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
  buyToken: '0x4200000000000000000000000000000000000006',
  sellAmount: '1000000', // 1 USDC
  chainId: '8453',
  taker: WALLET
})}`;

console.log('Fetching quote...');
const quoteRes = await fetch(quoteUrl, {
  headers: { '0x-api-key': API_KEY, '0x-version': 'v2' }
});
const quote = await quoteRes.json();

const txData = quote.transaction;
console.log('To:', txData.to);
console.log('Data:', txData.data?.slice(0, 50) + '...');

// Check USDC balance
const usdc = new ethers.Contract('0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913', [
  'function balanceOf(address) view returns (uint256)',
  'function approve(address spender, uint256 amount) returns (bool)',
  'function allowance(address owner, address spender) view returns (uint256)'
], wallet);

const balance = await usdc.balanceOf(WALLET);
console.log('USDC Balance:', Number(balance) / 1e6);

if (Number(balance) < 1000000) {
  console.log('Insufficient USDC!');
  process.exit(1);
}

// Check/set allowance  
const allowance = await usdc.allowance(WALLET, quote.allowanceTarget);
console.log('Allowance:', Number(allowance) / 1e6);

if (Number(allowance) < 1000000) {
  console.log('\nApproving...');
  const ap = await usdc.approve(quote.allowanceTarget, ethers.MaxUint256);
  await ap.wait();
  console.log('Approved! TX:', ap.hash);
}

// Execute
console.log('\nExecuting swap...');
const tx = {
  to: txData.to,
  data: txData.data,
  value: txData.value || '0',
  gasLimit: '300000'
};

const resp = await wallet.sendTransaction(tx);
console.log('Sent! TX:', resp.hash);

const receipt = await resp.wait();
console.log('\n✅ Success! Block:', receipt.blockNumber);
console.log('View: https://basescan.org/tx/', resp.hash);
