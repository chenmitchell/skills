const { createWalletClient, http } = require('viem');
const { privateKeyToAccount } = require('viem/accounts');
const { base } = require('viem/chains');

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

  console.log('=== Gasless Swap ===');

  // Get gasless quote
  const quoteUrl = `https://api.0x.org/gasless/quote?sellToken=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913&buyToken=0x4200000000000000000000000000000000000006&sellAmount=1000000&chainId=8453&taker=${WALLET}`;
  const quoteRes = await fetch(quoteUrl, {
    headers: { '0x-api-key': API_KEY, '0x-version': 'v2' }
  });
  const quote = await quoteRes.json();
  
  console.log('Trade type:', quote.trade.type);
  console.log('Original domain chainId:', quote.trade.eip712.domain.chainId, typeof quote.trade.eip712.domain.chainId);

  // Explicitly create domain as number
  const domain = {
    name: quote.trade.eip712.domain.name,
    chainId: 8453,
    verifyingContract: quote.trade.eip712.domain.verifyingContract
  };

  console.log('Fixed domain chainId:', domain.chainId, typeof domain.chainId);

  // Sign
  console.log('Signing...');
  const signature = await client.signTypedData({
    domain: domain,
    types: quote.trade.eip712.types,
    message: quote.trade.eip712.message,
    primaryType: quote.trade.eip712.primaryType
  });
  
  console.log('Signed!');

  // Split signature
  const sigBytes = signature.slice(2);
  const r = '0x' + sigBytes.slice(0, 64);
  const s = '0x' + sigBytes.slice(64, 128);
  const v = parseInt(sigBytes.slice(128, 130), 16);
  
  console.log('v:', v);

  // Build submit body
  const submitBody = {
    trade: {
      type: quote.trade.type,
      eip712: {
        domain: domain,
        types: quote.trade.eip712.types,
        message: quote.trade.eip712.message,
        primaryType: quote.trade.eip712.primaryType
      },
      signature: {
        v,
        r,
        s,
        signatureType: 2
      }
    }
  };

  const bodyStr = JSON.stringify(submitBody);
  console.log('Body chainId in JSON:', bodyStr.includes('8453'));

  console.log('Submitting...');
  const submitRes = await fetch('https://api.0x.org/gasless/submit', {
    method: 'POST',
    headers: { 
      '0x-api-key': API_KEY, 
      '0x-version': 'v2', 
      'Content-Type': 'application/json' 
    },
    body: bodyStr
  });

  const result = await submitRes.json();
  console.log('Result:', JSON.stringify(result, null, 2));
}

main().catch(e => console.error('Error:', e.message));
