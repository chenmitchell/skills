#!/usr/bin/env node
/**
 * BaseMail Setup Script
 * Creates a new wallet for AI agents who don't have one
 * 
 * Usage: node setup.js
 * 
 * ⚠️ IMPORTANT: This generates a new wallet with real funds capability.
 *    Keep your private key safe! Anyone with the key controls the wallet.
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const CONFIG_DIR = path.join(process.env.HOME, '.basemail');
const KEY_FILE = path.join(CONFIG_DIR, 'private-key');
const WALLET_FILE = path.join(CONFIG_DIR, 'wallet.json');

function prompt(question) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  return new Promise(resolve => {
    rl.question(question, answer => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

async function main() {
  console.log('🦞 BaseMail Wallet Setup');
  console.log('========================\n');

  // Check if wallet already exists
  if (fs.existsSync(KEY_FILE)) {
    const existing = fs.readFileSync(KEY_FILE, 'utf8').trim();
    const wallet = new ethers.Wallet(existing);
    console.log('⚠️  Wallet already exists!');
    console.log(`   Address: ${wallet.address}`);
    console.log(`   Key file: ${KEY_FILE}`);
    
    const answer = await prompt('\nCreate a NEW wallet? This will OVERWRITE the existing one! (yes/no): ');
    if (answer.toLowerCase() !== 'yes') {
      console.log('Cancelled.');
      process.exit(0);
    }
  }

  // Create config directory
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true, mode: 0o700 });
    console.log(`📁 Created ${CONFIG_DIR}`);
  }

  // Generate new wallet
  console.log('\n🔐 Generating new wallet...\n');
  const wallet = ethers.Wallet.createRandom();

  console.log('═'.repeat(60));
  console.log('🎉 NEW WALLET CREATED');
  console.log('═'.repeat(60));
  console.log(`\n📍 Address: ${wallet.address}`);
  console.log(`\n🔑 Private Key: ${wallet.privateKey}`);
  console.log(`\n📝 Mnemonic (12 words):\n   ${wallet.mnemonic.phrase}`);
  console.log('\n' + '═'.repeat(60));

  console.log('\n⚠️  IMPORTANT SECURITY NOTES:');
  console.log('   1. NEVER share your private key or mnemonic');
  console.log('   2. Anyone with these can steal your funds');
  console.log('   3. Back them up in a secure location');
  console.log('   4. The key file will be saved with restricted permissions (600)');

  const saveAnswer = await prompt('\nSave private key to ~/.basemail/private-key? (yes/no): ');
  
  if (saveAnswer.toLowerCase() === 'yes') {
    // Save private key (without 0x prefix for compatibility)
    fs.writeFileSync(KEY_FILE, wallet.privateKey, { mode: 0o600 });
    console.log(`\n✅ Private key saved to: ${KEY_FILE}`);
    
    // Also save wallet info (public only)
    const walletInfo = {
      address: wallet.address,
      created_at: new Date().toISOString(),
      note: 'Private key stored separately in private-key file',
    };
    fs.writeFileSync(WALLET_FILE, JSON.stringify(walletInfo, null, 2), { mode: 0o600 });
    console.log(`✅ Wallet info saved to: ${WALLET_FILE}`);
    
    console.log('\n📋 Next steps:');
    console.log('   1. Back up your mnemonic phrase somewhere safe');
    console.log('   2. Run: node register.js');
    console.log('   3. (Optional) Get a Basename at https://www.base.org/names');
    console.log('   4. (Optional) Run: node register.js --basename yourname.base.eth');
  } else {
    console.log('\n⚠️  Private key NOT saved.');
    console.log('   To use BaseMail, manually save your private key to:');
    console.log(`   ${KEY_FILE}`);
    console.log('   Or set environment variable: BASEMAIL_PRIVATE_KEY');
  }

  console.log('\n🦞 Setup complete!');
}

main().catch(err => {
  console.error('❌ Error:', err.message);
  process.exit(1);
});
