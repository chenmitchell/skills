const http = require('http');

const TOKEN = 'ta_08b295c6abb43e3a18fa36111f4dde9ba2aa44f9219efb660b12f23970eabeeb';
const TASK_ID = 'cmly7fnx50001v7li2mxh11ao';
// 八爪的 token 前缀 ta_2e731404... 需要先查到 agentId
// 先查木须工作区的 agents 找八爪

function api(path, method, body) {
  return new Promise((resolve, reject) => {
    const bodyStr = body ? JSON.stringify(body) : '';
    const options = {
      hostname: '118.195.138.220', port: 80, path, method,
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
        catch(e) { resolve({ status: res.statusCode, body: d }); }
      });
    });
    req.on('error', reject);
    if (bodyStr) req.write(bodyStr);
    req.end();
  });
}

async function main() {
  // 查 agents 找八爪的 agentId
  console.log('查询 agents...');
  const agentsRes = await api('/api/agents', 'GET');
  console.log('agents HTTP', agentsRes.status);
  if (agentsRes.body && agentsRes.body.agents) {
    const bazhua = agentsRes.body.agents.find(a => a.name && (a.name.includes('八爪') || a.name.toLowerCase().includes('bazhua')));
    console.log('八爪:', bazhua ? JSON.stringify({id: bazhua.id, name: bazhua.name}) : '未找到');
    // 列出所有 agents
    agentsRes.body.agents.forEach(a => console.log(' -', a.id, a.name, a.status));
  } else {
    console.log('agents response:', JSON.stringify(agentsRes.body).substring(0, 300));
  }

  // 查 task 的现有步骤
  const stepsRes = await api(`/api/tasks/${TASK_ID}/steps`, 'GET');
  console.log('\n任务步骤 HTTP', stepsRes.status);
  if (Array.isArray(stepsRes.body)) {
    console.log('步骤数:', stepsRes.body.length);
    stepsRes.body.forEach(s => console.log(' -', s.id, s.title, s.status));
  } else {
    console.log(JSON.stringify(stepsRes.body).substring(0, 200));
  }
}

main().catch(e => console.error('Error:', e.message));
