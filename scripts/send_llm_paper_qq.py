#!/usr/bin/env python3
"""
将LLM论文摘要发送到QQ
"""

import json
import os
import sys

# 输入文件路径
INPUT_FILE = "/home/admin/.openclaw/workspace/data/llm_paper_digest.json"
# QQ OpenID
QQ_OPENID = os.getenv('QQ_OPENID')

def load_papers():
    """加载论文数据"""
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 文件不存在: {INPUT_FILE}")
        return None

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data

def format_message(data):
    """格式化消息"""
    papers = data.get("papers", [])
    count = len(papers)
    generated_at = data.get("generated_at", "")

    if count == 0:
        return f"""📚 LLM论文日报
⏰ {generated_at}
━━━━━━━━━━━━━━━━━━
ℹ️ 最近7天未找到新的LLM论文
━━━━━━━━━━━━━━━━━━"""

    # 构建消息
    message = f"""📚 LLM论文日报
⏰ {generated_at}
📝 共{count}篇论文
━━━━━━━━━━━━━━━━━━

"""

    for i, paper in enumerate(papers, 1):
        title = paper['title']
        summary = paper['summary'][:200] + "..." if len(paper['summary']) > 200 else paper['summary']
        url = paper['url']

        message += f"{i}. {title}\n"
        message += f"   📅 {paper['published']}\n"
        message += f"   📝 摘要: {summary}\n"
        message += f"   🔗 {url}\n\n"

    message += "━━━━━━━━━━━━━━━━━━"
    return message

def save_to_qq(message):
    """保存消息到QQ发送目录"""
    # QQ Bot的消息发送目录
    qq_send_dir = "/home/admin/.openclaw/workspace/qq_messages"
    os.makedirs(qq_send_dir, exist_ok=True)

    # 生成文件名
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"llm_paper_{timestamp}.txt"
    filepath = os.path.join(qq_send_dir, filename)

    # 保存消息内容和目标
    message_data = {
        "to": QQ_OPENID,
        "message": message
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(message_data, f, ensure_ascii=False, indent=2)

    print(f"✓ 消息已保存到 {filepath}")
    print(f"✓ 目标用户: {QQ_OPENID}")
    return filepath

def print_message_preview(message):
    """打印消息预览"""
    print("\n" + "=" * 60)
    print("消息预览:")
    print("=" * 60)
    print(message)
    print("=" * 60)
    print(f"\n消息长度: {len(message)} 字符")

def main():
    print("=" * 60)
    print("LLM论文摘要发送到QQ")
    print("=" * 60)

    # 加载论文数据
    data = load_papers()
    if data is None:
        return 1

    # 格式化消息
    message = format_message(data)

    # 打印预览
    print_message_preview(message)

    # 保存到QQ发送目录
    save_to_qq(message)

    print("\n✓ 消息准备完成，等待发送...")
    return 0

if __name__ == "__main__":
    import datetime
    exit(main())