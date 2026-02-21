const { createWalletClient, http } = require('viem');
const { privateKeyToAccount } = require('viem/accounts');
const { base } = require('viem/chains');
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));

const API_KEY = 'e6eedf43-be5f-49e9-bb6c-8d9d5ce082d1';
const WALLET = '0x6581ff3C7D8dB9cFd7f8d34e0901d1151DAeC11E';
const PRIVATE_KEY = process.env.X402_KEY;

async function main() {
  const account = privateKeyToAccount(PRIVATE_KEY);
  const client = createWalletClient({
    chain: base,
    transport: http(),
    account
  });

  console.log('Wallet:', account.address);

  // Get gasless quote
  const quoteUrl = `https://api.0x.org/gasless/quote?sellToken=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913&buyToken=0x4200000000000000000000000000000000000006&sellAmount=1000000&chainId=8453&taker=${WALLET}`;
  const quoteRes = await fetch(quoteUrl, {
    headers: { '0x-api-key': API_KEY, '0x-version': 'v2' }
  });
  const quote = await quoteRes.json();
  
  console.log('Trade type:', quote.trade.type);
  console.log('Trade hash:', quote.trade.hash);

  // Sign the typed data
  console.log('\nSigning...');
  const signature = await client.signTypedData({
    domain: quote.trade.eip712.domain,
    types: quote.trade.eip712.types,
    message: quote.trade.eip712.message,
    primaryType: quote.trade.eip712.primaryType
  });
  
  console.log('Signature:', signature.slice(0, 20) + '...');
}

main().catch(e => console.error(e.message));
