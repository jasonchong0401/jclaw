#!/bin/bash
# 全球货币市场利率报告并发送到 QQ
# 使用 Tavily API 获取实时利率数据

echo "========================================"
echo "全球货币市场利率报告"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

# 进入工作目录
cd /home/admin/.openclaw/workspace

# 步骤1: 生成利率数据
echo ""
echo "步骤1: 获取利率数据..."
python3 scripts/global_interest_rates.py

if [ $? -ne 0 ]; then
    echo "❌ 数据获取失败"
    exit 1
fi

# 步骤2: 发送到QQ
echo ""
echo "步骤2: 发送到QQ..."

# 读取通知文件
if [ -f "data/qq_interest_rates_notify.json" ]; then
    message=$(python3 -c "import json; d=json.load(open('data/qq_interest_rates_notify.json')); print(d['message'])")

    # 使用 openclaw message 发送
    openclaw message send --channel qqbot --target "13E88D8A498827FBD0B939094DDCADFF" --message "$message"

    if [ $? -eq 0 ]; then
        echo "✅ 消息发送成功"
    else
        echo "❌ 消息发送失败"
        exit 1
    fi
else
    echo "❌ 未找到通知文件"
    exit 1
fi

echo ""
echo "========================================"
echo "任务完成"
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"