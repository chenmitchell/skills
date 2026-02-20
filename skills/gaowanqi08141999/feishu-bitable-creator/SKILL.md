---
name: feishu-bitable-creator
description: |
  Create and populate Feishu (Lark) Bitable (multidimensional tables) with automated cleanup.
  Use when the user needs to:
  1. Create a new Bitable from scratch with clean structure (no placeholder rows/columns)
  2. Batch create fields and records in a Bitable
  3. Convert structured data into a Bitable format
  4. Create data tables for research, comparison, or tracking purposes
  
  Automatically handles: empty placeholder row cleanup, default column removal, 
  intelligent primary field naming, and batch record creation.
---

# Feishu Bitable Creator

Creates clean, ready-to-use Feishu Bitable tables with automatic cleanup and data population.

## Why Use This Skill?

**Problem with default Bitable creation:**
- Feishu creates 10 empty placeholder rows by default
- Creates 4 default columns (文本, 单选, 日期, 附件) that are often unused
- Primary field is always named "文本" which is not descriptive

**This skill solves these issues:**
- ✅ Automatically deletes empty placeholder rows
- ✅ Removes unused default columns (keeps only primary field)
- ✅ Intelligently renames primary field based on table name
- ✅ Provides clean slate for your actual data

## Workflow

### Complete Creation Flow

```typescript
// Step 1: Create table with automatic cleanup
const table = await feishu_bitable_create_app({
  name: "项目名称清单"
});
// Returns: { app_token, url, table_id, primary_field_name }

// Step 2: Create custom fields
await feishu_bitable_create_field({
  app_token: table.app_token,
  table_id: table.table_id,
  field_name: "状态",
  field_type: 3  // SingleSelect
});

// Step 3: Add records
await feishu_bitable_create_record({
  app_token: table.app_token,
  table_id: table.table_id,
  fields: {
    [table.primary_field_name]: "项目A",  // Use dynamic field name
    "状态": "进行中"
  }
});

// Step 4: Return table URL to user
return table.url;
```

## Primary Field Naming Convention

The primary field is automatically renamed based on your table name:

| If table name contains | Primary field becomes |
|------------------------|----------------------|
| "项目" | "项目名称" |
| "研究" | "研究名称" |
| "测试" | "测试项" |
| "数据" | "数据项" |
| "任务" | "任务名称" |
| "记录" | "记录项" |
| Other (≤6 chars) | Use table name as-is |
| Other (>6 chars) | First 4 chars + "..." |

## Common Field Types

| Type ID | Name | Use For |
|---------|------|---------|
| 1 | Text | Names, descriptions |
| 2 | Number | Counts, amounts, IDs |
| 3 | SingleSelect | Status, priority, category |
| 4 | MultiSelect | Tags, skills, features |
| 5 | DateTime | Dates, deadlines |
| 7 | Checkbox | Done/Incomplete |
| 11 | User | Assignees, owners |

## Best Practices

### 1. Table Naming
- Use descriptive names that indicate content type
- Examples: "客户跟进表", "产品功能清单", "研究数据汇总"
- Avoid generic names like "表格1", "数据表"

### 2. Field Naming
- Use clear, concise names
- Examples: "优先级" not "P", "截止日期" not "Date"
- For SingleSelect fields, name reflects content: "状态", "分类"

### 3. Record Creation
- Always include the primary field value
- Use the returned `primary_field_name` from create_app
- Format values according to field type

### 4. Batch Operations
- Create all fields first, then add records
- For large datasets (>50 records), consider batching
- Use MultiSelect for tags/features that can have multiple values

## Complete Example: Research Data Table

```typescript
// Create research comparison table
const table = await feishu_bitable_create_app({
  name: "AI框架对比研究"
});

// Get table details
const meta = await feishu_bitable_get_meta({ url: table.url });
const tableId = meta.tables[0].table_id;

// Create fields
const fields = [
  { name: "框架名称", type: 1 },
  { name: "开发者", type: 1 },
  { name: "GitHub星标", type: 2 },
  { name: "核心特性", type: 1 },
  { name: "使用场景", type: 4 }
];

for (const field of fields) {
  await feishu_bitable_create_field({
    app_token: table.app_token,
    table_id: tableId,
    field_name: field.name,
    field_type: field.type
  });
}

// Add research data
const records = [
  {
    [table.primary_field_name]: "AutoGPT",
    "开发者": "Significant Gravitas",
    "GitHub星标": 157000,
    "核心特性": "自主递归任务执行",
    "使用场景": ["自动化研究", "数据分析"]
  },
  // ... more records
];

for (const record of records) {
  await feishu_bitable_create_record({
    app_token: table.app_token,
    table_id: tableId,
    fields: record
  });
}

return `Table created: ${table.url}`;
```

## Error Handling

Common issues and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| FieldNameNotFound | Wrong primary field name | Check `primary_field_name` in create_app result |
| 400 Bad Request | Invalid field type or value | Verify field_type ID and value format |
| Timeout | Too many records at once | Batch records in groups of 20-30 |

## Tips

1. **Check primary field name**: After create_app, the primary field name is returned in the result. Use this exact name when creating records.

2. **Multi-select values**: Pass as array: `["标签A", "标签B"]`

3. **Date fields**: Use timestamps or ISO strings

4. **Number fields**: Can use integers or decimals

5. **Field order**: Fields are created in the order you define them, except primary field is always first

## Output

Always return to user:
- ✅ Table URL
- ✅ Confirmation of data count
- ✅ Brief description of table structure