#!/usr/bin/env node
/**
 * BaseMail Send Email Script
 * 
 * Usage: node send.js <to> <subject> <body>
 * Example: node send.js alice@basemail.ai "Hello" "How are you?"
 */

const fs = require('fs');
const path = require('path');

const API_BASE = 'https://api.basemail.ai';
const TOKEN_FILE = path.join(process.env.HOME, '.basemail', 'token.json');

function getToken() {
  if (process.env.BASEMAIL_TOKEN) {
    return process.env.BASEMAIL_TOKEN;
  }
  
  if (!fs.existsSync(TOKEN_FILE)) {
    throw new Error('Not registered. Run register.js first.');
  }
  
  const data = JSON.parse(fs.readFileSync(TOKEN_FILE, 'utf8'));
  return data.token;
}

async function main() {
  const [to, subject, ...bodyParts] = process.argv.slice(2);
  const body = bodyParts.join(' ');

  if (!to || !subject) {
    console.log('Usage: node send.js <to> <subject> <body>');
    console.log('Example: node send.js alice@basemail.ai "Hello" "How are you?"');
    process.exit(1);
  }

  const token = getToken();

  console.log('📧 Sending email...');
  console.log(`To: ${to}`);
  console.log(`Subject: ${subject}`);

  const res = await fetch(`${API_BASE}/api/send`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ to, subject, body: body || '' }),
  });

  const data = await res.json();

  if (data.success) {
    console.log('\n✅ Sent!');
    console.log(`From: ${data.from}`);
    console.log(`Email ID: ${data.email_id}`);
  } else {
    console.error('\n❌ Failed:', data.error || data);
    process.exit(1);
  }
}

main().catch(err => {
  console.error('❌ Error:', err.message);
  process.exit(1);
});
