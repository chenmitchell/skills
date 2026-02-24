const http = require('http');
const TOKEN = 'ta_08b295c6abb43e3a18fa36111f4dde9ba2aa44f9219efb660b12f23970eabeeb';
const HUB = '118.195.138.220';

function api(path, method, body) {
  return new Promise((resolve, reject) => {
    const bodyStr = body ? JSON.stringify(body) : '';
    const options = {
      hostname: HUB, port: 80, path, method,
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + TOKEN, 'Content-Length': Buffer.byteLength(bodyStr) }
    };
    const req = http.request(options, (res) => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => { try { resolve({ status: res.statusCode, body: JSON.parse(d) }); } catch(e) { resolve({ status: res.statusCode, body: d }); } });
    });
    req.on('error', reject);
    if (bodyStr) req.write(bodyStr);
    req.end();
  });
}

const STEPS = [
  { id: 'cmlyq5w9q0003v71tgdq0uooj', title: '设计方案确认：两级审批模型' },
  { id: 'cmlyqdyuh0001v7uv7un5sct7', title: '步骤只能追加末尾，无法插入中间' },
  { id: 'cmlyqdz5i0003v7uve2dljvu8', title: '步骤内容 Markdown 不渲染' },
  { id: 'cmlyqdzg60005v7uv9mg8wgzu', title: '新建步骤缺少引导：执行人/附件/说明' },
];

async function main() {
  for (const s of STEPS) {
    const r = await api(`/api/steps/${s.id}/claim`, 'POST', {});
    console.log(`认领 [${s.title}]: ${r.body?.message || r.body?.error}`);
  }
}

main().catch(e => console.error(e.message));
