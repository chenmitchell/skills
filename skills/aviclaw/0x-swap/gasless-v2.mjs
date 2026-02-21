import fetch from 'node-fetch';

// Get quote
const quoteUrl = `https://api.0x.org/gasless/quote?sellToken=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913&buyToken=0x4200000000000000000000000000000000000006&sellAmount=1000000&chainId=8453&taker=0x6581ff3C7D8dB9cFd7f8d34e0901d1151DAeC11E`;
const quoteRes = await fetch(quoteUrl, {
  headers: { '0x-api-key': 'e6eedf43-be5f-49e9-bb6c-8d9d5ce082d1', '0x-version': 'v2' }
});
const quote = await quoteRes.json();

console.log('Quote type:', quote.trade?.type);

// Just output the quote for now - signing is complex
console.log('Quote:', JSON.stringify(quote.trade, null, 2).slice(0, 500));
