#!/bin/bash
# LLM 论文每日摘要 - 主执行脚本
# 功能: 1. 获取论文 2. 发送到QQ

echo "========================================"
echo "LLM 论文每日摘要任务"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

# 进入工作目录
cd /home/admin/.openclaw/workspace

# 步骤1: 生成论文摘要
echo ""
echo "步骤1: 生成论文摘要..."
python3 scripts/llm_paper_digest.py

if [ $? -ne 0 ]; then
    echo "❌ 论文摘要生成失败"
    exit 1
fi

# 步骤2: 发送到QQ
echo ""
echo "步骤2: 发送到QQ..."
python3 scripts/send_llm_paper_qq.py

if [ $? -ne 0 ]; then
    echo "❌ 消息发送失败"
    exit 1
fi

echo ""
echo "========================================"
echo "任务完成"
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"