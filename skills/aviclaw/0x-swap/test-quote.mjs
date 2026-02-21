import axios from 'axios';

// Try with different format - sellAmount as integer string
const params = new URLSearchParams();
params.append('sellToken', '0x4200000000000000000000000000000000000006');
params.append('buyToken', '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913');
params.append('sellAmount', '10000000');  // Small amount试试
params.append('chainId', '8453');

const url = `https://api.0x.org/swap/v1/price?${params.toString()}`;

try {
  const response = await axios.get(url);
  console.log('✅ Quote:', JSON.stringify(response.data, null, 2));
} catch (e) {
  console.log('Status:', e.response?.status);
  console.log('Error:', e.response?.data);
}
