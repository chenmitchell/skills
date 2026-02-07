#!/usr/bin/env node
/**
 * BaseMail Registration Script
 * Registers an AI agent for a @basemail.ai email address
 * 
 * Usage: node register.js [--basename yourname.base.eth]
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');
const https = require('https');

const API_BASE = 'https://api.basemail.ai';
const CONFIG_DIR = path.join(process.env.HOME, '.basemail');
const TOKEN_FILE = path.join(CONFIG_DIR, 'token.json');

// Get private key from env or file
function getPrivateKey() {
  if (process.env.BASEMAIL_PRIVATE_KEY) {
    return process.env.BASEMAIL_PRIVATE_KEY.trim();
  }
  
  const keyFile = path.join(CONFIG_DIR, 'private-key');
  if (fs.existsSync(keyFile)) {
    return fs.readFileSync(keyFile, 'utf8').trim();
  }
  
  // Fallback to common locations
  const fallbacks = [
    path.join(process.env.HOME, '.basemail', 'private-key'),
    path.join(process.cwd(), '.private-key'),
  ];
  
  for (const f of fallbacks) {
    if (fs.existsSync(f)) {
      return fs.readFileSync(f, 'utf8').trim();
    }
  }
  
  throw new Error('No private key found. Set BASEMAIL_PRIVATE_KEY or create ~/.basemail/private-key');
}

// Simple fetch wrapper
async function api(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  return res.json();
}

async function main() {
  // Parse args
  const args = process.argv.slice(2);
  let basename = null;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--basename' && args[i + 1]) {
      basename = args[i + 1];
    }
  }

  // Initialize wallet
  const privateKey = getPrivateKey();
  const wallet = new ethers.Wallet(privateKey);
  const address = wallet.address;

  console.log('🦞 BaseMail Registration');
  console.log('========================');
  console.log(`Wallet: ${address}`);
  if (basename) console.log(`Basename: ${basename}`);

  // Step 1: Start auth
  console.log('\n1️⃣ Starting authentication...');
  const startData = await api('/api/auth/start', {
    method: 'POST',
    body: JSON.stringify({ address }),
  });

  if (!startData.message) {
    console.error('❌ Failed to start auth:', startData);
    process.exit(1);
  }
  console.log('✅ Got SIWE message');

  // Step 2: Sign message
  console.log('\n2️⃣ Signing message...');
  const signature = await wallet.signMessage(startData.message);
  console.log('✅ Message signed');

  // Step 3: Verify
  console.log('\n3️⃣ Verifying signature...');
  const verifyData = await api('/api/auth/verify', {
    method: 'POST',
    body: JSON.stringify({
      address,
      message: startData.message,
      signature,
    }),
  });

  if (!verifyData.token) {
    console.error('❌ Verification failed:', verifyData);
    process.exit(1);
  }
  console.log('✅ Verified!');

  let token = verifyData.token;
  let email = verifyData.suggested_email;
  let handle = verifyData.handle;

  // Step 4: Register if needed
  if (!verifyData.registered) {
    console.log('\n4️⃣ Registering...');
    const regData = await api('/api/register', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify(basename ? { basename } : {}),
    });

    if (!regData.success) {
      console.error('❌ Registration failed:', regData);
      process.exit(1);
    }

    token = regData.token || token;
    email = regData.email;
    handle = regData.handle;
    console.log('✅ Registered!');
  }

  // Step 5: Upgrade if we have basename but got 0x handle
  if (basename && handle && handle.startsWith('0x')) {
    console.log('\n5️⃣ Upgrading to Basename...');
    const upgradeData = await api('/api/register/upgrade', {
      method: 'PUT',
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({ basename }),
    });

    if (upgradeData.success) {
      token = upgradeData.token || token;
      email = upgradeData.email;
      handle = upgradeData.handle;
      console.log('✅ Upgraded!');
    } else {
      console.log('⚠️ Upgrade failed:', upgradeData.error || upgradeData);
    }
  }

  // Save token
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true, mode: 0o700 });
  }
  
  const tokenData = {
    token,
    email,
    handle,
    wallet: address.toLowerCase(),
    basename: basename || null,
    saved_at: new Date().toISOString(),
  };
  
  fs.writeFileSync(TOKEN_FILE, JSON.stringify(tokenData, null, 2), { mode: 0o600 });

  console.log('\n🎉 Success!');
  console.log('============');
  console.log(`Email: ${email}`);
  console.log(`Token saved to: ${TOKEN_FILE}`);
}

main().catch(err => {
  console.error('❌ Error:', err.message);
  process.exit(1);
});
