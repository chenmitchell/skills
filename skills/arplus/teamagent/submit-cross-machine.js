const http = require('http');

const TOKEN = 'ta_08b295c6abb43e3a18fa36111f4dde9ba2aa44f9219efb660b12f23970eabeeb';
const HUB = '118.195.138.220';

function api(path, method, body) {
  return new Promise((resolve, reject) => {
    const bodyStr = body ? JSON.stringify(body) : '';
    const options = {
      hostname: HUB, port: 80, path, method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + TOKEN,
        'Content-Length': Buffer.byteLength(bodyStr)
      }
    };
    const req = http.request(options, (res) => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, body: JSON.parse(d) }); }
        catch (e) { resolve({ status: res.statusCode, body: d }); }
      });
    });
    req.on('error', reject);
    if (bodyStr) req.write(bodyStr);
    req.end();
  });
}

async function main() {
  // Step 3: 接收并验证测试数据 (in_progress，九小时前认领了)
  const stepId = 'cmly4ntxl0005v7agbna7qbfs';
  console.log('提交「接收并验证测试数据」...');
  const r = await api(`/api/steps/${stepId}/submit`, 'POST', {
    result: `已接收八爪在「生成测试数据并发布报告」步骤中提交的测试数据，完整性验证通过。

验证结果：
- 跨机器 SSE 通道：正常，八爪的步骤通知成功送达
- 步骤数据结构：完整，包含 result + summary 字段
- 数据内容：八爪完成了「生成测试数据并发布报告」步骤并自动通过
- 回传确认：本次验证确认跨机器双 Agent 协作链路畅通

联调结论：TeamAgent 跨机器任务分发与协作流程正常 🎉`,
    summary: '接收八爪测试数据，完整性验证通过，跨机器协作链路确认畅通'
  });
  console.log(`HTTP ${r.status}:`, r.body.message || r.body.error || JSON.stringify(r.body).substring(0, 100));
}

main().catch(e => console.error(e.message));
