import { ethers } from 'ethers';

const PRIVATE_KEY = process.env.X402_KEY;
const API_KEY = 'e6eedf43-be5f-49e9-bb6c-8d9d5ce082d1';
const WALLET = '0x6581ff3C7D8dB9cFd7f8d34e0901d1151DAeC11E';

const provider = new ethers.JsonRpcProvider('https://mainnet.base.org');
const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

console.log('=== Gasless Swap with Permit2 ===');
console.log('Wallet:', wallet.address);

// Get quote with Permit2
const quoteUrl = `https://api.0x.org/swap/permit2/quote?${new URLSearchParams({
  sellToken: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
  buyToken: '0x4200000000000000000000000000000000000006',
  sellAmount: '1000000',
  chainId: '8453',
  taker: WALLET
})}`;

console.log('Fetching Permit2 quote...');
const quoteRes = await fetch(quoteUrl, {
  headers: { '0x-api-key': API_KEY, '0x-version': 'v2' }
});
const quote = await quoteRes.json();

const txData = quote.transaction;
console.log('Transaction to:', txData.to);
console.log('Gas:', txData.gas);

// Build EIP-712 permit signature
const permit2 = quote.permit2;
const domain = {
  name: permit2.eip712.domain.name,
  chainId: permit2.eip712.domain.chainId,
  verifyingContract: permit2.eip712.domain.verifyingContract
};

const typedData = {
  domain,
  types: {
    TokenPermissions: [
      { name: 'token', type: 'address' },
      { name: 'amount', type: 'uint256' }
    ],
    PermitTransferFrom: [
      { name: 'permitted', type: 'TokenPermissions' },
      { name: 'spender', type: 'address' },
      { name: 'nonce', type: 'uint256' },
      { name: 'deadline', type: 'uint256' }
    ]
  },
  message: {
    permitted: permit2.eip712.message.permitted,
    spender: permit2.eip712.message.spender,
    nonce: permit2.eip712.message.nonce,
    deadline: permit2.eip712.message.deadline
  },
  primaryType: 'PermitTransferFrom'
};

console.log('\nSigning permit...');
const signature = await wallet.signTypedData(
  typedData.domain,
  typedData.types,
  typedData.message
);

// Permit2 requires: nonce, deadline, signature
// Build the permit data
const permitData = ethers.solidityPacked(
  ['uint256', 'uint256', 'bytes'],
  [permit2.eip712.message.nonce, permit2.eip712.message.deadline, signature]
);

// Append permit to transaction - the 0x contract expects it
const fullData = txData.data + permitData.slice(2);

console.log('Executing...');
const tx = await wallet.sendTransaction({
  to: txData.to,
  data: fullData,
  gasLimit: txData.gas
});

console.log('TX:', tx.hash);
const receipt = await tx.wait();
console.log('\n✅ Success! Block:', receipt.blockNumber);
console.log('View: https://basescan.org/tx/', tx.hash);
