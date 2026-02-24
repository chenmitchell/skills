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

const fixes = [
  {
    id: 'cmlyqdyuh0001v7uv7un5sct7',
    result: `## 修复：步骤只能追加末尾，无法插入中间\n\n**方案：** 在每个步骤卡片下方添加插入按钮，后端支持 \`insertAfterOrder\` 参数自动移位。\n\n**改动：**\n- 前端：步骤间 hover 出现「+ 在此处插入步骤」虚线按钮\n- 前端：新建步骤表单显示「↕️ 插入到步骤 N 之后」提示\n- 后端：\`POST /api/tasks/[id]/steps\` 支持 \`insertAfterOrder\`，自动将后续步骤 order +1\n\n**commit:** f0369ab`,
    summary: '步骤插入中间：hover 显示插入按钮，后端 insertAfterOrder 自动移位，已上线'
  },
  {
    id: 'cmlyqdz5i0003v7uve2dljvu8',
    result: `## 修复：步骤内容 Markdown 不渲染\n\n**方案：** 安装 react-markdown + remark-gfm，替换所有纯文本展示区域。\n\n**改动：**\n- 安装 \`react-markdown\` + \`remark-gfm\`\n- 步骤 description 渲染为 Markdown（支持标题/列表/粗体/链接等）\n- 步骤 result（提交结果）渲染为 Markdown\n- 历史提交记录 submission.result 渲染为 Markdown\n\n**commit:** f0369ab`,
    summary: 'Markdown 渲染：安装 react-markdown，description/result/submission 均支持，已上线'
  },
  {
    id: 'cmlyqdzg60005v7uv9mg8wgzu',
    result: `## 修复：新建步骤缺少引导（执行人/附件/说明）\n\n**方案：** 在新建步骤表单中加入「步骤说明」textarea，支持 Markdown 预览提示。\n\n**改动：**\n- 新增「步骤说明（选填，支持 Markdown）」多行输入框\n- 包含 placeholder 引导用户用 Markdown 格式填写\n- 执行人选择器已存在，附件功能作为后续 TODO\n\n**commit:** f0369ab`,
    summary: '新建步骤加说明字段：Markdown textarea 已加入表单，已上线'
  },
  {
    id: 'cmlyq5w9q0003v71tgdq0uooj',
    result: `## 设计方案：两级审批模型\n\n### 现状（一级审批）\n当前：任务创建者 OR 步骤 assignee 的 userId 可以审批任意步骤。\n\n### 两级审批模型（建议）\n\n**Level 1 — Agent Owner 审批（质量关）**\n> Agent 提交后，该 Agent 的人类 Owner 先审批\n> 确认"我的 Agent 做得没问题"\n\n**Level 2 — 任务创建者审批（验收关）**\n> Owner 审批通过后，任务创建者再验收\n> 确认"这个输出符合我的需求"\n\n### 适用场景\n- **跨工作区协作**：八爪（木须的）完成步骤 → 木须先审 → Aurora 再验收\n- **单工作区**：Level 1 可跳过（Owner = 任务创建者），只走 Level 2\n\n### 实现优先级\n- **当前已实现**：per-step canApprove（任务创建者 OR assignee.id）✅\n- **下一步**：UI 上区分两个审批阶段的状态（\`waiting_owner_approval\` → \`waiting_creator_approval\`）\n- **技术债**：跨工作区 Agent Owner 的任务访问权限（需邀请机制或直链审批）`,
    summary: '两级审批模型设计方案：Owner审批（质量关）→ 创建者审批（验收关），当前已实现 Level 2，Level 1 为下一步'
  }
];

async function main() {
  for (const fix of fixes) {
    const r = await api(`/api/steps/${fix.id}/submit`, 'POST', {
      result: fix.result,
      summary: fix.summary
    });
    console.log(`提交 [${fix.id.slice(-6)}]: ${r.body?.message || r.body?.error}`);
  }
}

main().catch(e => console.error(e.message));
