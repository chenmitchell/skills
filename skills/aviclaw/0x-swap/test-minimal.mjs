const body = JSON.stringify({
  trade: {
    type: "settler_metatransaction",
    eip712: {
      domain: {
        name: "Settler",
        chainId: 8453,
        verifyingContract: "0xdc5d8200a030798bc6227240f68b4dd9542686ef"
      },
      types: {},
      message: {},
      primaryType: "Test"
    },
    signature: {
      v: 27,
      r: "0x0000000000000000000000000000000000000000000000000000000000000001",
      s: "0x0000000000000000000000000000000000000000000000000000000000000002",
      signatureType: 2
    }
  }
});

console.log('Body:', body);

const res = await fetch('https://api.0x.org/gasless/submit', {
  method: 'POST',
  headers: { 
    '0x-api-key': 'e6eedf43-be5f-49e9-bb6c-8d9d5ce082d1', 
    '0x-version': 'v2', 
    'Content-Type': 'application/json' 
  },
  body
});

console.log(await res.json());
