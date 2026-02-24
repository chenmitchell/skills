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
  // 先查一下这两个 bug 步骤的 ID
  const stepsRes = await api('/api/my/available-steps', 'GET');
  const steps = stepsRes.body?.steps || stepsRes.body || [];
  const bugSteps = steps.filter(s => s.task?.title?.includes('Bug') && s.task?.title?.includes('审批'));
  console.log('Bug 步骤:', bugSteps.map(s => `${s.id} | ${s.title} | ${s.status}`));

  for (const step of bugSteps) {
    // claim
    const claimRes = await api(`/api/steps/${step.id}/claim`, 'POST', {});
    console.log(`认领 ${step.title}:`, claimRes.body?.message || claimRes.body?.error);
  }

  // 提交分析步骤
  const analyzeStep = bugSteps.find(s => s.title?.includes('分析'));
  if (analyzeStep) {
    const r = await api(`/api/steps/${analyzeStep.id}/submit`, 'POST', {
      result: `问题分析：跨工作区协作时审批按钮缺失

根本原因：
canApprove 当前逻辑 = session?.user?.id === task.creator?.id
只有任务创建者可以审批，不包含"步骤被分配者的人类（agent owner）"。

场景重现：
- Aurora 的工作区任务 → 分配给八爪（木须的 Agent）
- Aurora 能看到审批按钮（她是任务创建者）
- 木须看不到审批按钮（她不是任务创建者，且不在 Aurora 的工作区）

修复方案：
per-step canApprove = 任务创建者 OR 当前用户 = step.assignee.id（被分配者的 userId）

这样八爪完成的步骤，木须（step.assignee.id = 木须的 userId）也能看到审批按钮。
注：木须还需要能访问该任务（需要在工作区里，或通过通知直链进入）。`,
      summary: '根本原因：canApprove 只判断任务创建者，未考虑 agent owner。修复：per-step canApprove 加入 assignee.id 判断'
    });
    console.log('分析步骤提交:', r.body?.message || r.body?.error);
  }

  // 提交实施步骤
  const implStep = bugSteps.find(s => s.title?.includes('实施'));
  if (implStep) {
    const r = await api(`/api/steps/${implStep.id}/submit`, 'POST', {
      result: `已实施修复并部署至 http://118.195.138.220

代码改动（src/app/page.tsx）：
原来：canApprove={canApprove}
改为：canApprove={canApprove || currentUserId === step.assignee?.id}

效果：
- 任务创建者（Aurora）可以审批所有步骤 ✅
- 步骤被分配者的人类（如木须）也可以审批自己 Agent 的步骤 ✅
- 无法审批的人看到"⏳ 待 XX 审批"提示，而不是什么都没有 ✅

注意：木须需要能访问 Aurora 的任务页面才能实际操作审批（工作区权限问题，为后续 TODO）`,
      summary: 'per-step canApprove：加入 step.assignee.id 判断，agent owner 也可审批自己 agent 的步骤'
    });
    console.log('实施步骤提交:', r.body?.message || r.body?.error);
  }
}

main().catch(e => console.error(e.message));
