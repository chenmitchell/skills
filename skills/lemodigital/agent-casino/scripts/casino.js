#!/usr/bin/env node
// Agent Casino CLI — wraps casino.lemomo.xyz API
// Usage: node casino.js <command> [--wallet 0x...] [--choice rock|paper|scissors] [--amount N] [--id matchId]

const BASE_URL = process.env.CASINO_URL || 'https://casino.lemomo.xyz';

const args = process.argv.slice(2);
const command = args[0];

function getArg(name) {
  const idx = args.indexOf(`--${name}`);
  return idx !== -1 && args[idx + 1] ? args[idx + 1] : null;
}

async function request(method, path, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${BASE_URL}${path}`, opts);
  const data = await res.json();
  if (!res.ok) {
    console.error(`Error ${res.status}: ${data.message || JSON.stringify(data)}`);
    process.exit(1);
  }
  return data;
}

async function main() {
  const wallet = getArg('wallet');
  const choice = getArg('choice');
  const amount = getArg('amount');
  const id = getArg('id');

  switch (command) {
    case 'status': {
      if (!wallet) { console.error('--wallet required'); process.exit(1); }
      const d = await request('GET', `/status?wallet=${wallet}`);
      console.log(`Wallet:  ${d.wallet}`);
      console.log(`Balance: $${d.balance}`);
      console.log(`Locked:  $${d.lockedBalance}`);
      console.log(`Games:   ${d.gamesPlayed} (Won: ${d.gamesWon}, Rate: ${d.winRate})`);
      console.log(`Queue:   ${d.inQueue ? `Yes (${d.queueId})` : 'No'}`);
      break;
    }
    case 'deposit': {
      if (!wallet || !amount) { console.error('--wallet and --amount required'); process.exit(1); }
      const d = await request('POST', '/deposit', { wallet, amount: parseFloat(amount) });
      console.log(`Deposited $${amount}. New balance: $${d.balance}`);
      break;
    }
    case 'play': {
      if (!wallet || !choice) { console.error('--wallet and --choice required'); process.exit(1); }
      const d = await request('POST', '/play', { wallet, choice });
      if (d.match) {
        const m = d.match;
        const you = m.player1 === wallet ? 'player1' : 'player2';
        const yourChoice = you === 'player1' ? m.player1Choice : m.player2Choice;
        const oppChoice = you === 'player1' ? m.player2Choice : m.player1Choice;
        const result = m.result === 'draw' ? 'TIE' : m.result === you ? 'WIN' : 'LOSE';
        const payout = you === 'player1' ? m.player1Payout : m.player2Payout;
        console.log(`Matched! You: ${yourChoice} vs Opponent: ${oppChoice} → ${result}`);
        console.log(`Payout: $${payout}`);
      } else {
        console.log(`Queued in ${d.pool} pool. Queue ID: ${d.queueId}`);
        console.log(`Balance: $${d.balance}, Locked: $${d.lockedBalance}`);
      }
      break;
    }
    case 'match': {
      if (!id) { console.error('--id required'); process.exit(1); }
      const d = await request('GET', `/match/${id}`);
      console.log(`Match:   ${d.id} (${d.status})`);
      console.log(`Player1: ${d.player1} → ${d.player1Choice} (payout: $${d.player1Payout})`);
      console.log(`Player2: ${d.player2} → ${d.player2Choice} (payout: $${d.player2Payout})`);
      console.log(`Result:  ${d.result}`);
      break;
    }
    case 'leaderboard': {
      const d = await request('GET', '/leaderboard');
      if (!d.length) { console.log('No players yet.'); break; }
      console.log('Rank  Wallet                                      Won   Rate    Earned');
      d.forEach((p, i) => {
        const w = p.wallet.slice(0, 10) + '...' + p.wallet.slice(-4);
        console.log(`#${i + 1}    ${w}  ${String(p.gamesWon).padStart(4)}  ${p.winRate.padStart(5)}  $${p.totalEarned}`);
      });
      break;
    }
    case 'withdraw': {
      if (!wallet || !amount) { console.error('--wallet and --amount required'); process.exit(1); }
      const d = await request('POST', '/withdraw', { wallet, amount: parseFloat(amount) });
      console.log(`Withdrawn $${amount}. New balance: $${d.newBalance}`);
      break;
    }
    case 'forfeit': {
      if (!wallet) { console.error('--wallet required'); process.exit(1); }
      const d = await request('POST', '/forfeit', { wallet });
      console.log(`Forfeited $${d.forfeited}. Balance: $${d.balance}`);
      break;
    }
    default:
      console.log('Agent Casino CLI');
      console.log('Commands: status, deposit, play, match, leaderboard, withdraw, forfeit');
      console.log('Options:  --wallet 0x... --choice rock|paper|scissors --amount N --id matchId');
      console.log('Env:      CASINO_URL (default: https://casino.lemomo.xyz)');
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
