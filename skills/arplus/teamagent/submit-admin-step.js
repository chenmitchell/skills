const { TeamAgentClient } = require('./teamagent-client.js');
const http = require('http');

process.env.TEAMAGENT_TOKEN = 'ta_08b295c6abb43e3a18fa36111f4dde9ba2aa44f9219efb660b12f23970eabeeb';
process.env.TEAMAGENT_HUB = 'http://118.195.138.220';

const client = new TeamAgentClient();

// 手动发起步骤提交（admin page step）
async function submitStep(stepId, result, summary) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ result, summary });
    const options = {
      hostname: '118.195.138.220',
      port: 80,
      path: `/api/steps/${stepId}/submit`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.TEAMAGENT_TOKEN}`,
        'Content-Length': Buffer.byteLength(body)
      }
    };
    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        console.log(`HTTP ${res.statusCode}:`, data.substring(0, 200));
        resolve(data);
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

// 创建新任务（用 agent token 试试）
async function createTask(workspaceId, title, description) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ workspaceId, title, description, mode: 'solo', priority: 'high' });
    const options = {
      hostname: '118.195.138.220',
      port: 80,
      path: '/api/tasks',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.TEAMAGENT_TOKEN}`,
        'Content-Length': Buffer.byteLength(body)
      }
    };
    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        console.log(`创建任务 HTTP ${res.statusCode}:`, data.substring(0, 400));
        resolve(JSON.parse(data));
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

async function main() {
  // 提交 admin 页面步骤
  const adminStepId = 'cmly4viry000lv7ag9k2l0tlh';
  console.log('提交后台管理页面步骤...');
  await submitStep(adminStepId,
    `后台管理页面 /admin 已完成并部署\n\n功能：总览指标卡/Agent状态/任务趋势图/用户列表/全平台任务总览，权限控制完成（仅 aurora@arplus.top）`,
    '后台管理页面 /admin 已上线，访问 http://118.195.138.220/admin'
  );

  // 尝试用 agent token 创建任务
  console.log('\n尝试创建测试任务...');
  const workspaceId = 'cmly2cr2w0001v7scp3orkepg'; // 木须的工作区（八爪在那里）
  await createTask(workspaceId,
    '🧪 全面验收测试：移动端 + 后台 + 核心流程',
    `测试范围：
1. 移动端适配（手机浏览器）：侧边栏自动收起/展开、iOS Safari视口、返回按钮
2. 后台管理页面 /admin：总览/用户列表/任务总览，数据是否正确
3. 核心流程：任务创建→Solo拆解→步骤认领→执行→提交→审批全流程
4. 申诉机制：提交→被打回→申诉→审核

执行人：八爪（木须工作区）
验收标准：每项测试写明通过/失败/问题描述`
  );
}

main();
