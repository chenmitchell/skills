import axios from 'axios';

const API_KEY = 'e6eedf43-be5f-49e9-bb6c-8d9d5ce082d1';

const url = 'https://api.0x.org/swap/v1/price?sellToken=ETH&buyToken=USDC&sellAmount=1000000000000000000&chainId=8453';

console.log('Testing 0x API...');

try {
  const response = await axios.get(url, { 
    headers: { '0x-api-key': API_KEY } 
  });
  console.log('\n✅ Quote received!');
  console.log(response.data);
} catch (e) {
  console.error('Error:', e.response?.status, e.response?.data || e.message);
}
