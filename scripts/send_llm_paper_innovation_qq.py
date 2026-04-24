#!/usr/bin/env python3
"""
将LLM论文创新点分析发送到QQ
"""

import json
import os
import sys
from datetime import datetime

# 输入文件路径
INNOVATIONS_FILE = "/home/admin/.openclaw/workspace/data/llm_paper_innovations.json"
# QQ OpenID（从环境变量读取）
QQ_OPENID = "13E88D8A498827FBD0B939094DDCADFF"  # 根据cron任务提供

def load_innovations():
    """加载创新点分析数据"""
    if not os.path.exists(INNOVATIONS_FILE):
        print(f"❌ 文件不存在: {INNOVATIONS_FILE}")
        return None

    with open(INNOVATIONS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data

def format_innovation_message(data):
    """格式化创新点消息"""
    papers = data.get("papers", [])
    evaluation = data.get("evaluation", {})
    count = len(papers)

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

    for i, item in enumerate(papers, 1):
        title = item['title']
        innovation = item['innovation']

        message += f"{i}. {title}\n"
        message += f"   ❓ 核心问题: {innovation['core_problem']}\n"
        message += f"   💡 主要创新: {innovation['main_innovation']}\n"

        if innovation.get('tech_highlights'):
            message += f"   ⚙️ 技术亮点:\n"
            for highlight in innovation['tech_highlights']:
                message += f"      • {highlight}\n"

        message += "\n"

    # 添加趋势总结
    if evaluation:
        message += "━━━━━━━━━━━━━━━━━━\n"
        if evaluation.get('most_noteworthy'):
            message += f"🏆 最值得注意: {evaluation['most_noteworthy'][:50]}...\n\n"
        if evaluation.get('trends'):
            message += "📈 趋势观察:\n"
            for trend in evaluation['trends'][:3]:
                message += f"   • {trend}\n"
        message += "\n"

    message += "━━━━━━━━━━━━━━━━━━"

    return message

def save_to_qq(message):
    """保存消息到QQ发送目录"""
    # QQ Bot的消息发送目录
    qq_send_dir = "/home/admin/.openclaw/workspace/qq_messages"
    os.makedirs(qq_send_dir, exist_ok=True)

    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"llm_paper_innovation_{timestamp}.txt"
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
    print("LLM论文创新点发送到QQ")
    print("=" * 60)

    # 加载创新点分析数据
    data = load_innovations()
    if data is None:
        return 1

    # 格式化消息
    message = format_innovation_message(data)

    # 打印预览
    print_message_preview(message)

    # 保存到QQ发送目录
    save_to_qq(message)

    print("\n✓ 消息准备完成，等待发送...")
    return 0

if __name__ == "__main__":
    exit(main())