const { TeamAgentClient } = require('./teamagent-client.js');

process.env.TEAMAGENT_TOKEN = 'ta_08b295c6abb43e3a18fa36111f4dde9ba2aa44f9219efb660b12f23970eabeeb';
process.env.TEAMAGENT_HUB = 'http://118.195.138.220';

const client = new TeamAgentClient();

async function main() {
  // 重新提交「通知测试」步骤（之前乱码被打回）
  const notifyStepId = 'cmlxnkpc6001iv7wclax98fhg';
  console.log('重新提交「通知测试」步骤...');

  try {
    await client.claimStep(notifyStepId);
    console.log('认领成功');
  } catch(e) {
    console.log('认领失败（可能已认领）:', e.message);
  }

  const resultText = `Aurora，移动端适配已完成，可以去测试啦！访问 http://118.195.138.220

本次优化内容：
1. 移动端自动检测：初始 sidebarCollapsed 根据屏幕宽度(<768px)动态设置，新增 resize 监听，横竖屏自适应
2. /team 页面：Banner 和数据栏内边距移动端优化，px-6 改 px-4 sm:px-6
3. 长标题截断：添加 max-w-[calc(100vw-2rem)] 防止溢出
4. 任务标题：添加 max-w-[calc(100vw-1rem)] 截断
5. /agent 页面：px-6 改 px-4 sm:px-6 移动端优化
6. iOS Safari 视口修复：h-screen 改 h-[100svh] 防止地址栏遮挡

请在手机浏览器访问 http://118.195.138.220 验收！`;

  try {
    const r = await client.submitStep(notifyStepId, resultText, {
      summary: '移动端适配完成：自动检测+resize监听+返回按钮+iOS svh修复，共6项优化'
    });
    console.log('提交成功:', JSON.stringify(r));
  } catch(e) {
    console.error('提交失败:', e.message);
  }
}

main();
