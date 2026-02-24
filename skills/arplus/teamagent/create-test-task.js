const { TeamAgentClient } = require('./teamagent-client.js');

process.env.TEAMAGENT_TOKEN = 'ta_08b295c6abb43e3a18fa36111f4dde9ba2aa44f9219efb660b12f23970eabeeb';
process.env.TEAMAGENT_HUB = 'http://118.195.138.220';

const client = new TeamAgentClient();

async function main() {
  // 1. 提交「开发后台管理页面」步骤
  const adminStepId = 'cmly4viry000lv7ag9k2l0tlh';
  console.log('提交「开发后台管理页面」步骤...');
  try {
    await client.claimStep(adminStepId);
  } catch(e) {
    console.log('认领状态:', e.message);
  }
  try {
    const r = await client.submitStep(adminStepId,
      `后台管理页面 /admin 已完成并部署到 http://118.195.138.220/admin

功能清单：
- 总览 Tab：系统指标卡片（用户数/Agent数/工作区/任务总数/完成率/待审批）
- Agent 状态分布：实时在线/working/offline 状态
- 近7天任务趋势图（柱状图）
- 步骤统计（总数/已完成/待审批）
- 用户 & Agent Tab：用户列表，含 Agent 配对状态、工作区、任务步骤数
- 任务总览 Tab：全平台任务，支持状态筛选（全部/待开始/进行中/已完成）
- 权限控制：仅 aurora@arplus.top 可访问，其他人重定向到 /tasks`,
      { summary: '后台管理页面 /admin 已上线：总览指标/Agent状态/任务总览，权限控制完成' }
    );
    console.log('后台页面步骤提交成功:', r.message);
  } catch(e) {
    console.error('提交失败:', e.message);
  }

  // 2. 创建给八爪的测试任务
  console.log('\n创建八爪测试任务...');
  try {
    // 先获取工作区ID
    const wsRes = await client.request('GET', '/api/workspaces/my');
    console.log('工作区:', JSON.stringify(wsRes));
  } catch(e) {
    console.error('获取工作区失败:', e.message);
  }
}

main();
