#!/usr/bin/env node
// Generate new TOTP secret and QR code
const { authenticator } = require('@otplib/preset-default');
const QRCode = require('qrcode');

const service = process.argv[2] || 'OpenClaw';
const account = process.argv[3] || 'admin';

// Generate new secret (base32)
const secret = authenticator.generateSecret();
console.log('New TOTP_SECRET:');
console.log(secret);

// Generate Google Authenticator URL
const otpauth = authenticator.keyuri(account, service, secret);

console.log('\nURI for Google Authenticator/Authy:');
console.log(otpauth);

// Generate QR code
QRCode.toString(otpauth, { type: 'utf8', small: true }, (err, qr) => {
  if (!err) {
    console.log('\nQR Code (ASCII):\n');
    console.log(qr);
  }

  console.log('\nManual setup:');
  console.log('1. Open Google Authenticator/Authy');
  console.log('2. Tap "+" > "Enter a setup key"');
  console.log(`3. Account: ${account}`);
  console.log('4. Key:', secret);
  console.log('5. Type: Time-based (TOTP)');

  console.log('\nAdd this line to your .env:');
  console.log(`TOTP_SECRET=${secret}`);

  console.log('\nDone. Configure your authenticator app before using.');
});
