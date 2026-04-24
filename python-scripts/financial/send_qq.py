#!/usr/bin/env python3
"""
发送金融数据到QQ
直接使用 OpenClaw message 工具
"""

import json
import os

def send_financial_report():
    """发送金融数据报告到QQ"""

    # 读取通知文件
    notify_file = '/home/admin/.openclaw/workspace/data/qq_financial_notify.json'

    if not os.path.exists(notify_file):
        print(f"❌ 未找到通知文件: {notify_file}")
        return False

    with open(notify_file, 'r', encoding='utf-8') as f:
        notify_data = json.load(f)

    message = notify_data['message']
    qq_openid = os.environ.get('QQ_OPENID')

    if not qq_openid:
        print("❌ 未找到 QQ_OPENID 环境变量")
        return False

    print(f"发送消息到 QQ ({qq_openid})...")

    # 注意：这个脚本会由 OpenClaw 的 session 调用
    # message 工具在环境中是可用的
    # 我们需要返回消息内容让 OpenClaw 处理

    print("✅ 消息准备就绪")
    print(f"消息长度: {len(message)} 字符")

    # 输出到标准输出，便于 bash 脚本捕获
    print(f"__MESSAGE_START__")
    print(message)
    print(f"__MESSAGE_END__")

    return True

if __name__ == '__main__':
    success = send_financial_report()
    exit(0 if success else 1)