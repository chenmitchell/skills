#!/usr/bin/env node
/**
 * BaseMail Inbox Script
 * 
 * Usage: 
 *   node inbox.js              # List inbox
 *   node inbox.js <email_id>   # Read specific email
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

async function listInbox(token) {
  const res = await fetch(`${API_BASE}/api/inbox`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  
  const data = await res.json();
  
  if (data.error) {
    console.error('❌ Error:', data.error);
    process.exit(1);
  }

  console.log(`📬 Inbox (${data.unread} unread / ${data.total} total)`);
  console.log('='.repeat(60));

  if (data.emails.length === 0) {
    console.log('No emails.');
    return;
  }

  for (const email of data.emails) {
    const unread = email.read ? ' ' : '●';
    const date = new Date(email.created_at * 1000).toLocaleString();
    console.log(`${unread} [${email.id}]`);
    console.log(`  From: ${email.from_addr}`);
    console.log(`  Subject: ${email.subject}`);
    console.log(`  Date: ${date}`);
    console.log(`  Preview: ${email.snippet?.slice(0, 80)}...`);
    console.log('');
  }
}

async function readEmail(token, emailId) {
  const res = await fetch(`${API_BASE}/api/inbox/${emailId}`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  
  const data = await res.json();
  
  if (data.error) {
    console.error('❌ Error:', data.error);
    process.exit(1);
  }

  console.log('📧 Email');
  console.log('='.repeat(60));
  console.log(`From: ${data.from_addr}`);
  console.log(`To: ${data.to_addr}`);
  console.log(`Subject: ${data.subject}`);
  console.log(`Date: ${new Date(data.created_at * 1000).toLocaleString()}`);
  console.log('='.repeat(60));
  console.log(data.body);
}

async function main() {
  const emailId = process.argv[2];
  const token = getToken();

  if (emailId) {
    await readEmail(token, emailId);
  } else {
    await listInbox(token);
  }
}

main().catch(err => {
  console.error('❌ Error:', err.message);
  process.exit(1);
});
