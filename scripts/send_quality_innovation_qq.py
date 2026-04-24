#!/usr/bin/env python3
"""
发送高质量LLM论文创新日报到QQ
"""

import json
import os
from datetime import datetime

# 输入文件路径（高质量中文分析）
HIGH_QUALITY_FILE = "/home/admin/.openclaw/workspace/data/llm_paper_innovation.json"
# QQ OpenID
QQ_OPENID = "13E88D8A498827FBD0B939094DDCADFF"

def load_innovations():
    """加载创新点分析数据"""
    if not os.path.exists(HIGH_QUALITY_FILE):
        print(f"❌ 文件不存在: {HIGH_QUALITY_FILE}")
        return None

    with open(HIGH_QUALITY_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data

def format_innovation_message(data):
    """格式化创新点消息（高质量中文版）"""
    papers = data.get("papers", [])
    count = len(papers)
    generated_at = data.get("generated_at", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    if count == 0:
        return f"""📚 LLM论文创新日报
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━
ℹ️ 最近未找到新的LLM论文
━━━━━━━━━━━━━━━━━━"""

    # 构建消息
    message = f"""📚 LLM论文创新日报
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📝 共{count}篇论文
━━━━━━━━━━━━━━━━━━

"""

    for i, paper in enumerate(papers, 1):
        title = paper.get('title', '未知标题')
        innovations = paper.get('innovation', [])
        url = paper.get('url', '')

        message += f"{i}. {title}\n"
        message += f"   🔗 {url}\n"

        if innovations:
            message += f"   💡 创新点:\n"
            for innovation in innovations[:3]:  # 每篇论文最多3个创新点
                message += f"      • {innovation}\n"

        message += "\n"

    message += "━━━━━━━━━━━━━━━━━━"

    return message

def save_to_qq(message):
    """保存消息到QQ发送目录"""
    qq_send_dir = "/home/admin/.openclaw/workspace/qq_messages"
    os.makedirs(qq_send_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"llm_paper_innovation_high_quality_{timestamp}.txt"
    filepath = os.path.join(qq_send_dir, filename)

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
    print("LLM论文创新点发送到QQ（高质量中文版）")
    print("=" * 60)

    data = load_innovations()
    if data is None:
        return 1

    message = format_innovation_message(data)
    print_message_preview(message)
    save_to_qq(message)

    print("\n✓ 消息准备完成，等待发送...")
    return 0

if __name__ == "__main__":
    exit(main())