const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));

async function main() {
  const API_KEY = 'e6eedf43-be5f-49e9-bb6c-8d9d5ce082d1';
  const WALLET = '0x6581ff3C7D8dB9cFd7f8d34e0901d1151DAeC11E';

  // Get quote first
  const quoteRes = await fetch(
    `https://api.0x.org/gasless/quote?sellToken=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913&buyToken=0x4200000000000000000000000000000000000006&sellAmount=1000000&chainId=8453&taker=${WALLET}`,
    { headers: { '0x-api-key': API_KEY, '0x-version': 'v2' } }
  );
  const quote = await quoteRes.json();

  console.log('Quote chainId type:', typeof quote.trade.eip712.domain.chainId);
  console.log('Quote chainId value:', quote.trade.eip712.domain.chainId);

  // Test with chainId at ROOT level
  const testCases = [
    {
      name: 'chainId at root',
      body: {
        chainId: 8453,
        trade: {
          type: quote.trade.type,
          eip712: {
            domain: quote.trade.eip712.domain,
            types: quote.trade.eip712.types,
            message: quote.trade.eip712.message,
            primaryType: quote.trade.eip712.primaryType
          },
          signature: { v: 27, r: '0x0000000000000000000000000000000000000000000000000000000000000001', s: '0x0000000000000000000000000000000000000000000000000000000000000002', signatureType: 2 }
        }
      }
    },
    {
      name: 'chainId at root and hash',
      body: {
        chainId: 8453,
        tradeHash: quote.trade.hash,
        trade: {
          type: quote.trade.type,
          eip712: {
            domain: quote.trade.eip712.domain,
            types: quote.trade.eip712.types,
            message: quote.trade.eip712.message,
            primaryType: quote.trade.eip712.primaryType
          },
          signature: { v: 27, r: '0x0000000000000000000000000000000000000000000000000000000000000001', s: '0x0000000000000000000000000000000000000000000000000000000000000002', signatureType: 2 }
        }
      }
    },
    {
      name: 'chainId and approval (full)',
      body: {
        chainId: 8453,
        trade: {
          type: quote.trade.type,
          hash: quote.trade.hash,
          eip712: {
            domain: quote.trade.eip712.domain,
            types: quote.trade.eip712.types,
            message: quote.trade.eip712.message,
            primaryType: quote.trade.eip712.primaryType
          },
          signature: { v: 27, r: '0x0000000000000000000000000000000000000000000000000000000000000001', s: '0x0000000000000000000000000000000000000000000000000000000000000002', signatureType: 2 }
        }
      }
    }
  ];

  for (const tc of testCases) {
    console.log(`\n=== Testing: ${tc.name} ===`);
    console.log('Request body:', JSON.stringify(tc.body, null, 2).slice(0, 1000));
    const res = await fetch('https://api.0x.org/gasless/submit', {
      method: 'POST',
      headers: { '0x-api-key': API_KEY, '0x-version': 'v2', 'Content-Type': 'application/json' },
      body: JSON.stringify(tc.body)
    });
    const result = await res.json();
    console.log('Status:', res.status);
    console.log('Response:', JSON.stringify(result, null, 2).slice(0, 500));
  }
}

main().catch(e => console.error(e));
