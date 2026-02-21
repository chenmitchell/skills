import { createWalletClient, http } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { base } from 'viem/chains';
import { signTypedData } from 'viem/utils';

const PRIVATE_KEY = process.env.X402_KEY;
const API_KEY = 'e6eedf43-be5f-49e9-bb6c-8d9d5ce082d1';
const WALLET = '0x6581ff3C7D8dB9cFd7f8d34e0901d1151DAeC11E';

const account = privateKeyToAccount(PRIVATE_KEY);

console.log('=== Gasless Swap with viem ===');

// Get gasless quote
const quoteUrl = `https://api.0x.org/gasless/quote?${new URLSearchParams({
  sellToken: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
  buyToken: '0x4200000000000000000000000000000000000006',
  sellAmount: '1000000',
  chainId: '8453',
  taker: WALLET
})}`;

const quoteRes = await fetch(quoteUrl, {
  headers: { '0x-api-key': API_KEY, '0x-version': 'v2' }
});
const quote = await quoteRes.json();

console.log('Trade type:', quote.trade.type);

// Sign using viem's signTypedData
const signature = await signTypedData({
  account,
  domain: quote.trade.eip712.domain,
  types: quote.trade.eip712.types,
  message: quote.trade.eip712.message,
  primaryType: quote.trade.eip712.primaryType
});

console.log('Signed!');

// Submit
const sigBytes = signature.slice(2);
const r = '0x' + sigBytes.slice(0, 64);
const s = '0x' + sigBytes.slice(64, 128);
const v = parseInt(sigBytes.slice(128, 130), 16) + 27;

const submitBody = {
  trade: {
    type: quote.trade.type,
    eip712: quote.trade.eip712,
    signature: { v, r, s, signatureType: 2 }
  }
};

const submitRes = await fetch('https://api.0x.org/gasless/submit', {
  method: 'POST',
  headers: { '0x-api-key': API_KEY, '0x-version': 'v2', 'Content-Type': 'application/json' },
  body: JSON.stringify(submitBody)
});

const result = await submitRes.json();
console.log('Result:', result);
