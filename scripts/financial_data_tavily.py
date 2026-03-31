#!/usr/bin/env python3
"""
获取金融数据脚本（使用 Tavily 的 include-answer 功能）
直接获取答案，无需抓取网页
"""

import json
import re
import subprocess
from datetime import datetime

# Tavily 脚本路径
TAVILY_SCRIPT = "/home/admin/.openclaw/workspace/skills/tavily-search/skill/scripts/tavily_search.py"

# 金融数据配置
FINANCIAL_DATA = {
    'XAU/USD': {
        'name': '黄金价格',
        'query': 'What is the current gold price per ounce in USD?',
        'pattern': r'[\$]\s*([0-9,]+\.?[0-9]*)\s*(?:USD)?',
        'unit': '$',
        'decimal': 2
    },
    'US10Y': {
        'name': '美国10年期国债利率',
        'query': 'What is the current US 10 year treasury yield?',
        'pattern': r'([0-9.]+)%',
        'unit': '%',
        'decimal': 3
    },
    'US2Y': {
        'name': '2年期美国国债',
        'query': 'What is the current US 2 year treasury yield?',
        'pattern': r'([0-9.]+)%',
        'unit': '%',
        'decimal': 3
    },
    'SOFR': {
        'name': 'SOFR利率',
        'query': 'What is the current SOFR rate?',
        'pattern': r'([0-9.]+)%',
        'unit': '%',
        'decimal': 3
    },
    'XAG/USD': {
        'name': '白银价格',
        'query': 'What is the current silver price per ounce in USD?',
        'pattern': r'[\$]\s*([0-9,]+\.?[0-9]*)\s*(?:USD)?',
        'unit': '$',
        'decimal': 2
    },
    'CL/USD': {
        'name': '原油期货价格(WTI)',
        'query': 'What is the current WTI crude oil price per barrel in USD?',
        'pattern': r'[\$]\s*([0-9,]+\.?[0-9]*)\s*(?:USD)?',
        'unit': '$',
        'decimal': 2
    },
    'VIX': {
        'name': 'VIX恐慌指数',
        'query': 'What is the current VIX index level?',
        'pattern': r'([0-9.]+)',
        'unit': '',
        'decimal': 2
    },
    'USD/CNY': {
        'name': '美元人民币汇率',
        'query': 'What is the current USD to CNY exchange rate?',
        'pattern': r'([0-9.]+)',
        'unit': 'CNY',
        'decimal': 4
    },
    'EUR/USD': {
        'name': '欧元美元汇率',
        'query': 'What is the current EUR to USD exchange rate?',
        'pattern': r'([0-9.]+)',
        'unit': '',
        'decimal': 4
    }
}


def get_tavily_answer(query: str) -> dict:
    """使用 Tavily 获取答案"""
    try:
        cmd = [
            "python3", TAVILY_SCRIPT,
            "--query", query,
            "--max-results", "3",
            "--include-answer",
            "--format", "raw"
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        output = result.stdout.decode('utf-8', errors='ignore')

        if result.returncode == 0 and output:
            try:
                data = json.loads(output)
                return {
                    'success': True,
                    'answer': data.get('answer', ''),
                    'results': data.get('results', [])
                }
            except json.JSONDecodeError:
                return {'success': False, 'error': 'Invalid JSON'}
        return {'success': False, 'error': 'Tavily request failed'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def extract_price_from_answer(answer: str, pattern: str) -> float:
    """从答案中提取价格"""
    if not answer:
        return None

    try:
        # 清理答案文本
        cleaned = re.sub(r'[^\x00-\x7F]+', '', answer)  # 移除非ASCII字符

        # 查找匹配
        matches = re.findall(pattern, cleaned, re.IGNORECASE)
        if matches:
            # 取第一个匹配
            value_str = matches[0].replace(',', '')
            value = float(value_str)

            # 验证合理性
            if 0 < value < 1000000:  # 防止异常值
                return value
    except Exception as e:
        print(f"    提取失败: {e}")
        return None

    return None


def extract_price_from_results(results: list, pattern: str) -> float:
    """从搜索结果中提取价格"""
    if not results:
        return None

    for result in results:
        content = result.get('content', '')
        if content:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                try:
                    value_str = matches[0].replace(',', '')
                    value = float(value_str)
                    if 0 < value < 1000000:
                        return value
                except:
                    continue

    return None


def get_financial_data(symbol: str, config: dict) -> dict:
    """获取单个金融数据"""
    print(f"  获取 {config['name']} ({symbol})...")
    print(f"    查询: {config['query']}")

    # 获取 Tavily 答案
    response = get_tavily_answer(config['query'])

    if not response['success']:
        print(f"    ✗ 查询失败: {response.get('error', 'Unknown error')}")
        return {
            'symbol': symbol,
            'name': config['name'],
            'success': False,
            'error': response.get('error', '查询失败')
        }

    # 尝试从答案中提取
    answer = response['answer']
    print(f"    答案: {answer[:100]}...")

    price = extract_price_from_answer(answer, config['pattern'])

    # 如果答案中没有，尝试从搜索结果中提取
    if price is None:
        results = response.get('results', [])
        price = extract_price_from_results(results, config['pattern'])

    if price:
        print(f"    ✓ 成功: {price:.{config['decimal']}f}{config['unit']}")
        return {
            'symbol': symbol,
            'name': config['name'],
            'price': price,
            'unit': config['unit'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'answer': answer,
            'success': True
        }
    else:
        print(f"    ✗ 无法提取价格")
        return {
            'symbol': symbol,
            'name': config['name'],
            'success': False,
            'error': '无法提取价格',
            'answer': answer
        }


def main():
    """主函数"""
    results = {
        'timestamp': datetime.now().isoformat(),
        'data': {}
    }

    print("="*80)
    print("获取金融数据（使用 Tavily AI）")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # 获取所有数据
    for symbol, config in FINANCIAL_DATA.items():
        data = get_financial_data(symbol, config)
        results['data'][symbol] = data
        print()  # 空行分隔

    # 打印结果
    print("="*80)
    print("数据汇总")
    print("="*80)

    success_count = 0
    failed_count = 0

    for symbol, data in results['data'].items():
        if data['success']:
            success_count += 1
            price = data['price']
            unit = data['unit']
            decimal = FINANCIAL_DATA[symbol]['decimal']
            print(f"  ✓ {data['name']}: {price:.{decimal}f}{unit}")
        else:
            failed_count += 1
            print(f"  ✗ {data['name']}: {data.get('error', '失败')}")

    # 保存完整结果
    output_file = '/home/admin/.openclaw/workspace/data/financial_data_tavily.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 生成通知消息
    message = f"""📊 金融数据报告
━━━━━━━━━━━━━━━━━━
🕐 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📡 数据源: Tavily AI 搜索

【实时数据】
"""

    for symbol, data in results['data'].items():
        if data['success']:
            price = data['price']
            unit = data['unit']
            decimal = FINANCIAL_DATA[symbol]['decimal']
            message += f"✓ {data['name']}: {price:.{decimal}f}{unit}\n"
        else:
            message += f"✗ {data['name']}: {data.get('error', '失败')}\n"

    if success_count > 0:
        message += f"\n✅ 成功获取: {success_count} 项"
    if failed_count > 0:
        message += f"\n❌ 失败: {failed_count} 项"

    message += "\n━━━━━━━━━━━━━━━━━━"

    # 保存通知消息
    notify_file = '/home/admin/.openclaw/workspace/data/qq_financial_notify.json'
    notify_data = {
        'timestamp': datetime.now().isoformat(),
        'message': message,
        'results': results
    }
    with open(notify_file, 'w', encoding='utf-8') as f:
        json.dump(notify_data, f, ensure_ascii=False, indent=2)

    print(f"\n完整数据: {output_file}")
    print(f"QQ通知: {notify_file}")

    print("\n📱 消息预览:")
    print("-" * 80)
    print(message)
    print("-" * 80)


if __name__ == '__main__':
    main()