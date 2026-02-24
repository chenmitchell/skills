#!/usr/bin/env node
/**
 * TeamAgent Solo Mode 轮询脚本
 * 每个 OpenClaw 子 Agent 在 HEARTBEAT 时运行此脚本
 * 用法: node poll-tasks.js [--token ta_xxx] [--url http://localhost:3000]
 */

const args = process.argv.slice(2)
const getArg = (flag) => {
  const i = args.indexOf(flag)
  return i !== -1 ? args[i + 1] : null
}

const TOKEN = getArg('--token') || process.env.TEAMAGENT_TOKEN
const BASE_URL = getArg('--url') || process.env.TEAMAGENT_URL || process.env.TEAMAGENT_HUB || 'http://localhost:3000'

if (!TOKEN) {
  console.error('❌ 需要提供 token: --token ta_xxx 或 TEAMAGENT_TOKEN 环境变量')
  process.exit(1)
}

async function api(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${TOKEN}`,
      'Content-Type': 'application/json',
      ...(options.headers || {})
    }
  })
  return { status: res.status, ok: res.ok, data: await res.json() }
}

async function main() {
  // 1. 查询我的待处理步骤
  const { ok, data } = await api('/api/agent/my-steps')
  
  if (!ok) {
    console.error('❌ 无法连接 TeamAgent:', data)
    process.exit(1)
  }

  if (data.count === 0) {
    console.log('✅ 无待处理步骤')
    process.exit(0)
  }

  console.log(`📋 发现 ${data.count} 个待处理步骤`)
  
  for (const step of data.steps) {
    console.log(`\n→ Step ${step.order}: ${step.title} [${step.status}]`)
    console.log(`  任务: ${step.task.title}`)
    if (step.rejectionReason) {
      console.log(`  ⚠️  打回原因: ${step.rejectionReason}`)
    }
    console.log(`  操作: ${step.status === 'pending' ? step.actions.claim : step.actions.submit}`)
  }

  // 输出结构化 JSON 供 Agent 读取
  console.log('\n📊 JSON 数据:')
  console.log(JSON.stringify({
    hasTasks: true,
    count: data.count,
    steps: data.steps.map(s => ({
      id: s.id,
      order: s.order,
      title: s.title,
      status: s.status,
      taskTitle: s.task.title,
      taskDescription: s.task.description,
      description: s.description,
      skills: s.skills,
      inputs: s.inputs,
      rejectionReason: s.rejectionReason,
      claimUrl: s.actions.claim,
      submitUrl: s.actions.submit
    }))
  }, null, 2))
}

main().catch(e => {
  console.error('❌ 错误:', e.message)
  process.exit(1)
})
