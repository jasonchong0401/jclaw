#!/usr/bin/env python3
"""
发送金融数据到QQ
简化版本，直接调用 message 工具
"""

import json
import os

# 读取通知文件
notify_file = '/home/admin/.openclaw/workspace/data/qq_financial_notify.json'

with open(notify_file, 'r', encoding='utf-8') as f:
    notify_data = json.load(f)

message = notify_data['message']
qq_openid = os.environ.get('QQ_OPENID')

print(f"发送消息到 QQ ({qq_openid})...")

# 打印消息内容以便调试
print("消息内容:")
print("-" * 80)
print(message)
print("-" * 80)

# 这里我们假设 message 工具已经在环境中可用
# 我们将通过 subprocess 调用它
import subprocess

result = subprocess.run([
    '/opt/openclaw/node_modules/.pnpm/openclaw@2026.3.2_@napi-rs+canvas@0.1.95_@types+express@5.0.6_audio-decode@2.2.3_hono@4_f3ad5634f0c5b8a7671ba65ac99bfd49/node_modules/.bin/openclaw',
    'message', 'send',
    '--channel', 'qqbot',
    '--target', qq_openid,
    '--message', message
], capture_output=True, text=True, timeout=30)

print(result.stdout)
if result.stderr:
    print("错误:", result.stderr, file=sys.stderr)

exit(result.returncode)