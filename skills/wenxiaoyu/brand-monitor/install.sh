#!/bin/bash

# OpenClaw 品牌监控 Skill 安装脚本
# 只复制必需的文件

set -e

echo "🚀 开始安装 brand-monitor skill..."

# 检查是否在正确的目录
if [ ! -f "SKILL.md" ]; then
    echo "❌ 错误：请在 brand-monitor-skill 目录下运行此脚本"
    exit 1
fi

# 目标目录
TARGET_DIR="$HOME/.openclaw/skills/brand-monitor"

# 创建目标目录
echo "📁 创建目标目录..."
mkdir -p "$TARGET_DIR/prompts"

# 复制必需文件
echo "📋 复制必需文件..."
cp SKILL.md "$TARGET_DIR/"
cp config.example.json "$TARGET_DIR/"
cp prompts/monitor.md "$TARGET_DIR/prompts/"
cp prompts/alert.md "$TARGET_DIR/prompts/"
cp prompts/analyze-trend.md "$TARGET_DIR/prompts/"

# 验证安装
echo ""
echo "✅ 安装完成！"
echo ""
echo "📂 已安装的文件："
ls -lh "$TARGET_DIR/"
echo ""
ls -lh "$TARGET_DIR/prompts/"
echo ""

# 提示下一步
echo "📝 下一步："
echo "1. 创建配置文件："
echo "   cd $TARGET_DIR"
echo "   cp config.example.json config.json"
echo "   nano config.json"
echo ""
echo "2. 重启 OpenClaw："
echo "   openclaw restart"
echo ""
echo "3. 验证安装："
echo "   openclaw skills list | grep brand-monitor"
echo ""
echo "🎉 祝使用愉快！"
