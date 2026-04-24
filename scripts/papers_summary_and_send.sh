#!/bin/bash
# 论文总结并发送到 QQ
# 每天早上8点自动总结论文并发送详细分析

echo "========================================"
echo "论文总结任务"
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

echo "QQ OpenID: $QQ_OPENID"

# 步骤1: 分析论文并生成总结
echo ""
echo "步骤1: 分析论文..."
python3 python-scripts/papers/summarize_papers.py

SUMMARY_EXIT_CODE=$?

if [ $SUMMARY_EXIT_CODE -ne 0 ]; then
    echo "❌ 论文分析失败，退出任务"
    exit 1
fi

# 步骤2: 发送到QQ（每篇论文一条消息）
echo ""
echo "步骤2: 发送到QQ..."

# 使用 Python 发送多条消息
python3 <<'PYTHON_SCRIPT'
import subprocess
import os
import json
import sys

# 确保环境变量已设置
if 'QQ_OPENID' not in os.environ:
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
notify_file = '/home/admin/.openclaw/workspace/data/paper_summary_notify.json'
with open(notify_file, 'r', encoding='utf-8') as f:
    notify_data = json.load(f)

messages = notify_data.get('messages', [])
count = len(messages)

print("准备发送 {} 条论文总结消息".format(count))

# 发送每条消息
success_count = 0
for i, message in enumerate(messages, 1):
    print("\n发送第 {}/{} 条消息...".format(i, count))
    print("消息长度: {} 字符".format(len(message)))

    result = subprocess.run([
        '/opt/openclaw/node_modules/.pnpm/node_modules/.bin/openclaw',
        'message', 'send',
        '--channel', 'qqbot',
        '--target', qq_openid,
        '--message', message
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)

    stdout = result.stdout.decode('utf-8', errors='ignore')
    if stdout:
        print(stdout)

    stderr = result.stderr.decode('utf-8', errors='ignore')
    if stderr:
        print("错误输出:", stderr, file=sys.stderr)

    if result.returncode == 0:
        print("✅ 第 {} 条消息发送成功".format(i))
        success_count += 1
    else:
        print("❌ 第 {} 条消息发送失败，返回码: {}".format(i, result.returncode))
        # 继续发送下一条

print("\n========================================")
print("发送完成: {}/{} 条消息成功".format(success_count, count))
print("========================================")

if success_count == count:
    sys.exit(0)
else:
    sys.exit(1)
PYTHON_SCRIPT

SEND_EXIT_CODE=$?

if [ $SEND_EXIT_CODE -eq 0 ]; then
    echo "✅ 所有消息发送成功"
else
    echo "⚠️  部分消息发送失败"
    exit 1
fi

echo ""
echo "========================================"
echo "任务完成"
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"