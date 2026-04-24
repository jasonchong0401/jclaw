#!/usr/bin/env python3
"""
发送金融数据到QQ
直接使用 OpenClaw 的 message 工具
"""

import sys
import json
import os

def main():
    """主函数"""
    # 读取通知文件
    notify_file = '/home/admin/.openclaw/workspace/data/qq_financial_notify.json'

    if not os.path.exists(notify_file):
        print(f"❌ 未找到通知文件: {notify_file}")
        return 1

    with open(notify_file, 'r', encoding='utf-8') as f:
        notify_data = json.load(f)

    message = notify_data['message']
    qq_openid = os.environ.get('QQ_OPENID')

    if not qq_openid:
        print("❌ 未找到 QQ_OPENID 环境变量")
        return 1

    print(f"准备发送消息到 QQ ({qq_openid})...")
    print(f"消息长度: {len(message)} 字符")

    # 导入 OpenClaw 的 message 工具
    # 这里我们使用环境变量和系统调用
    import subprocess

    try:
        result = subprocess.run([
            sys.executable, '-c',
            '''
import sys
sys.path.insert(0, "/opt/openclaw")

# 动态导入 message 工具
from openclaw import message

# 读取环境变量
channel = "qqbot"
target = "''' + qq_openid + '''"
message_text = """''' + message.replace('"""', '\\"""') + '''"""

# 发送消息
result = message(
    action="send",
    channel=channel,
    target=target,
    message=message_text
)

print(json.dumps(result, ensure_ascii=False, indent=2))
'''
        ], capture_output=True, text=True, timeout=60)

        print(result.stdout)

        if result.stderr:
            print("错误输出:", result.stderr, file=sys.stderr)

        if result.returncode == 0:
            print("✅ 消息发送成功")
            return 0
        else:
            print(f"❌ 消息发送失败，返回码: {result.returncode}")
            return 1

    except subprocess.TimeoutExpired:
        print("❌ 消息发送超时")
        return 1
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())