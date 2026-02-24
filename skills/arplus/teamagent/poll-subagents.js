#!/usr/bin/env node
/**
 * TeamAgent 子 Agent 步骤轮询脚本
 * Lobster HEARTBEAT 调用，检测子 Agent 是否有 pending 步骤需要执行
 * 输出 JSON 告诉 Lobster 应该 spawn 哪些子 Agent
 */

const BASE_URL = process.env.TEAMAGENT_URL || 'http://localhost:3000'

// 🌊 水族军团 — 深海无声，代码不停
const SUB_AGENTS = [
  {
    name: 'Inkfish 小毛🦑',
    role: 'docwriter',
    token: 'ta_ca76a74dbeef38c40f33c07e64b9b03ee85021fb64f3108edc4a6aae301475be',
    capabilities: ['writing', 'documentation', 'content'],
    spawnInstructions: '你是 Inkfish 小毛🦑（原 Quill），水族军乌贼文书官，专注文档写作。请检查 TeamAgent 分配给你的步骤并执行。'
  },
  {
    name: 'PufferQA🐡',
    role: 'testrunner',
    token: 'ta_adfe75818da5c88188e98bbeddfb8864886b964a86a2366df2328e84938b3f76',
    capabilities: ['testing', 'qa', 'debugging'],
    spawnInstructions: '你是 PufferQA🐡（原 TestRunner），水族军河豚测试官，专注测试和质量保证。请检查 TeamAgent 分配给你的步骤并执行。'
  },
  {
    name: 'Mantis🦐',
    role: 'codereviewer',
    token: 'ta_a905e14b9854d5bb86442b8d44ec63844690cdcb58bd6d343aa0c86b073b70cc',
    capabilities: ['code-review', 'architecture', 'security'],
    spawnInstructions: '你是 Mantis🦐（原 CodeReviewer），水族军螳螂虾审计官，专注代码审查。请检查 TeamAgent 分配给你的步骤并执行。'
  },
  {
    name: 'Nautilus📡',
    role: 'devops',
    token: 'ta_bca50006cb6c55615b738f43ebbc42f8753b4d2eb47f9c831500200682cccd9e',
    capabilities: ['deployment', 'monitoring', 'devops'],
    spawnInstructions: '你是 Nautilus📡（原 DevOps），水族军鹦鹉螺运维，专注部署和运维。请检查 TeamAgent 分配给你的步骤并执行。'
  }
]

async function checkAgent(agent) {
  try {
    const res = await fetch(`${BASE_URL}/api/agent/my-steps`, {
      headers: { 'Authorization': `Bearer ${agent.token}` }
    })
    if (!res.ok) return { agent: agent.name, error: res.status, steps: [] }
    const data = await res.json()
    return {
      agent: agent.name,
      role: agent.role,
      token: agent.token,
      spawnInstructions: agent.spawnInstructions,
      count: data.count,
      steps: data.steps || []
    }
  } catch (e) {
    return { agent: agent.name, error: e.message, steps: [] }
  }
}

async function main() {
  const results = await Promise.all(SUB_AGENTS.map(checkAgent))

  const needsSpawn = results.filter(r => r.count > 0)
  const allClear = needsSpawn.length === 0

  if (allClear) {
    console.log('✅ 所有子 Agent 无待处理步骤')
    console.log(JSON.stringify({ needsSpawn: false, agents: [] }))
    process.exit(0)
  }

  console.log(`🚨 ${needsSpawn.length} 个子 Agent 有待处理步骤！`)
  for (const r of needsSpawn) {
    console.log(`  ${r.agent}: ${r.count} 个步骤`)
    for (const s of r.steps) {
      const rejection = s.rejectionReason ? ` (打回: ${s.rejectionReason})` : ''
      console.log(`    Step ${s.order} [${s.status}]: ${s.title}${rejection}`)
    }
  }

  console.log('\n📊 JSON 数据:')
  console.log(JSON.stringify({
    needsSpawn: true,
    agents: needsSpawn.map(r => ({
      name: r.agent,
      role: r.role,
      token: r.token,
      spawnInstructions: r.spawnInstructions,
      count: r.count,
      steps: r.steps.map(s => ({
        id: s.id,
        order: s.order,
        title: s.title,
        status: s.status,
        taskTitle: s.task?.title,
        taskId: s.task?.id,
        description: s.description,
        rejectionReason: s.rejectionReason,
        claimUrl: s.actions?.claim,
        submitUrl: s.actions?.submit
      }))
    }))
  }, null, 2))
}

main().catch(e => {
  console.error('❌ 错误:', e.message)
  process.exit(1)
})
