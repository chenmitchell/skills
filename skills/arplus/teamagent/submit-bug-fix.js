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

async function main() {
  const analyzeId = 'cmlypbvt80005v7wyl3j64zco';
  const implId = 'cmlypbvtc0009v7wy5u8k4kn7';

  // 认领 + 提交 分析步骤
  await api(`/api/steps/${analyzeId}/claim`, 'POST', {});
  let r = await api(`/api/steps/${analyzeId}/submit`, 'POST', {
    result: `问题分析：跨工作区协作时审批按钮缺失

根本原因：
canApprove 逻辑 = session.user.id === task.creator.id
只有任务创建者可审批，不包含"步骤 assignee 的人类（agent owner）"。

场景：Aurora 的工作区任务 → 分配给八爪（木须的 Agent）
- Aurora 能看到审批按钮（任务创建者）✅
- 木须看不到审批按钮（不是创建者，且不在 Aurora 工作区）❌

修复方向：per-step canApprove = 任务创建者 OR currentUserId === step.assignee.id`,
    summary: '根本原因：canApprove 只判断任务创建者，未考虑 agent owner。修复：per-step 加入 assignee.id 判断'
  });
  console.log('分析步骤:', r.body?.message || r.body?.error);

  // 认领 + 提交 实施步骤
  await api(`/api/steps/${implId}/claim`, 'POST', {});
  r = await api(`/api/steps/${implId}/submit`, 'POST', {
    result: `已实施修复并部署至 http://118.195.138.220

代码改动（src/app/page.tsx）：
Before: canApprove={canApprove}
After:  canApprove={canApprove || currentUserId === step.assignee?.id}

效果：
✅ 任务创建者（Aurora）可审批所有步骤
✅ 步骤 assignee 的人类（如木须）也可审批自己 Agent 的步骤
✅ 无法审批的人看到"⏳ 待 XX 审批"提示

commit: bf180bf
注：木须需要能访问 Aurora 的任务才能实际操作（工作区权限为后续 TODO）`,
    summary: 'per-step canApprove 修复上线：agent owner 可审批自己 agent 的步骤，commit bf180bf'
  });
  console.log('实施步骤:', r.body?.message || r.body?.error);
}

main().catch(e => console.error(e.message));
