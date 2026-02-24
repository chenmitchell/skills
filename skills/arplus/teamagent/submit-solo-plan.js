const { TeamAgentClient } = require('./teamagent-client.js');

process.env.TEAMAGENT_TOKEN = 'ta_08b295c6abb43e3a18fa36111f4dde9ba2aa44f9219efb660b12f23970eabeeb';
process.env.TEAMAGENT_HUB = 'http://118.195.138.220';

const client = new TeamAgentClient();

async function main() {
  const stepId = 'cmly4viru000hv7agefimw9cc'; // Solo模式测试任务拆解

  const resultText = `## Solo 模式测试计划

### 1. 主 Agent 任务拆解流程测试
- 创建新任务（Solo模式）
- 验证 Lobster 自动收到 decompose 步骤通知（SSE）
- Lobster 认领 decompose 步骤，调 LLM 拆解为子步骤
- 验证子步骤自动分配给对应 Agent（按 assignee 字段）
- 验证 parallelGroup 步骤同时变为可认领状态

### 2. 步骤认领、执行、提交流程测试
- Agent 认领分配给自己的步骤
- 执行步骤（写入 result）
- 提交步骤结果
- 验证状态变更：pending → in_progress → waiting_approval / done

### 3. requiresApproval 审批流程测试
- 提交需要审批的步骤
- 验证步骤变为 waiting_approval
- Aurora 审批通过 → 下游步骤自动解锁
- Aurora 打回 → 步骤回到 pending，Agent 可重做

### 4. 申诉（Appeal）机制测试
- 步骤被打回后，Agent 发起申诉（提供原因）
- 主 Agent（Lobster）收到申诉通知
- Lobster 审核：通过申诉 or 维持打回
- 验证申诉状态流转：appeal_pending → appeal_approved / appeal_rejected

### 5. 跨机器步骤分发测试（Lobster ↔ 八爪）
- 木须工作区建任务，步骤分配给 Lobster（Aurora机器）和 八爪（木须机器）
- 验证两台机器的 Agent 都能收到 SSE 通知
- 验证步骤结果在机器间正确传递

### 测试执行人
- Solo 模式拆解：Lobster（主 Agent）
- 申诉测试：Lobster 提交申诉，Lobster 自己审核（测试闭环）
- 跨机器测试：Lobster + 八爪

### 预期输出
- Solo模式测试报告（含每项通过/失败/备注）
- 发现的 Bug 清单`;

  try {
    const r = await client.submitStep(stepId, resultText, {
      summary: 'Solo模式测试计划：5大测试项，覆盖拆解/认领/提交/审批/申诉/跨机器分发'
    });
    console.log('Solo测试计划提交成功:', r.message);
  } catch(e) {
    console.error('提交失败:', e.message);
  }
}

main();
