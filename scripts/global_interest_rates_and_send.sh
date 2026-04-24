#!/bin/bash
# 全球货币市场利率报告并发送到 QQ
# 使用 Tavily API 获取实时利率数据

echo "========================================"
echo "全球货币市场利率报告"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

# 进入工作目录
cd /home/admin/.openclaw/workspace

# 加载环境变量
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# 检查 QQ OpenID
if [ -z "$QQ_OPENID" ]; then
    echo "❌ 未找到 QQ_OPENID 环境变量"
    exit 1
fi

# 步骤1: 生成利率数据
echo ""
echo "步骤1: 获取利率数据..."
python3 python-scripts/financial/global_interest_rates.py

if [ $? -ne 0 ]; then
    echo "❌ 数据获取失败"
    exit 1
fi

# 步骤2: 发送到QQ
echo ""
echo "步骤2: 发送到QQ..."

# 使用 Python 发送消息（确保环境变量正确传递）
python3 <<'PYTHON_SCRIPT'
import subprocess
import os
import json
import sys

# 确保环境变量已设置
if 'QQ_OPENID' not in os.environ:
    # 从 .env 文件读取
    env_file = '/home/admin/.openclaw/workspace/.env'
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

qq_openid = os.environ.get('QQ_OPENID')
print("QQ OpenID: {}".format(qq_openid))

# 读取通知文件
notify_file = '/home/admin/.openclaw/workspace/data/qq_interest_rates_notify.json'
with open(notify_file, 'r', encoding='utf-8') as f:
    notify_data = json.load(f)

message = notify_data['message']
print("消息长度: {} 字符".format(len(message)))

# 调用 OpenClaw message CLI
result = subprocess.run([
    '/opt/openclaw/node_modules/.pnpm/node_modules/.bin/openclaw',
    'message', 'send',
    '--channel', 'qqbot',
    '--target', qq_openid,
    '--message', message
], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)

# 输出结果
stdout = result.stdout.decode('utf-8', errors='ignore')
if stdout:
    print(stdout)

stderr = result.stderr.decode('utf-8', errors='ignore')
if stderr:
    print("错误输出:", stderr, file=sys.stderr)

if result.returncode == 0:
    print("✅ 消息发送成功")
    sys.exit(0)
else:
    print("❌ 消息发送失败，返回码: {}".format(result.returncode))
    sys.exit(1)
PYTHON_SCRIPT

SEND_EXIT_CODE=$?

if [ $SEND_EXIT_CODE -eq 0 ]; then
    echo "✅ 消息发送成功"
else
    echo "❌ 消息发送失败"
    exit 1
fi

echo ""
echo "========================================"
echo "任务完成"
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"