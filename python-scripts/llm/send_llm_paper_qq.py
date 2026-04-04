#!/usr/bin/env python3
"""
发送 LLM 论文摘要到 QQ
"""

import json
import subprocess

# 目标QQ openid
TARGET_QQ = "13E88D8A498827FBD0B939094DDCADFF"


def send_to_qq(message: str):
    """发送消息到QQ"""
    try:
        # 使用 openclaw message 命令发送
        cmd = [
            "openclaw", "message", "send",
            "--channel", "qqbot",
            "--target", f"qqbot:c2c:{TARGET_QQ}",
            "--message", message
        ]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        output = result.stdout.decode('utf-8', errors='ignore')
        error = result.stderr.decode('utf-8', errors='ignore')

        return result.returncode == 0, output, error

    except Exception as e:
        return False, "", str(e)


def main():
    """主函数"""
    # 读取生成的报告
    notify_file = "/home/admin/.openclaw/workspace/data/qq_llm_paper_notify.json"

    try:
        with open(notify_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        message = data.get("message", "")
        if not message:
            print("❌ 没有找到消息内容")
            return

        # 发送到QQ
        print("📱 发送消息到QQ...")
        success, output, error = send_to_qq(message)

        if success:
            print("✅ 消息发送成功")
            if output:
                print(f"   {output}")
        else:
            print(f"❌ 消息发送失败")
            if error:
                print(f"   错误: {error}")

    except FileNotFoundError:
        print(f"❌ 文件不存在: {notify_file}")
        print("   请先运行 llm_paper_digest.py 生成报告")
    except Exception as e:
        print(f"❌ 发送失败: {e}")


if __name__ == "__main__":
    main()