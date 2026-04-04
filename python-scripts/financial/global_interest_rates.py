#!/usr/bin/env python3
"""
获取全球主要国家货币市场利率并保存到数据库
使用 Tavily API 获取实时利率数据
"""

import json
import re
import subprocess
import sqlite3
from datetime import datetime

# Tavily 脚本路径
TAVILY_SCRIPT = "/home/admin/.openclaw/workspace/skills/tavily-search/skill/scripts/tavily_search.py"

# 数据库路径
DB_PATH = '/home/admin/.openclaw/workspace/data/interest_rates.db'


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


def extract_rate_from_answer(answer: str, pattern: str) -> float:
    """从答案中提取利率"""
    if not answer:
        return None

    try:
        cleaned = re.sub(r'[^\x00-\x7F]+', '', answer)
        matches = re.findall(pattern, cleaned, re.IGNORECASE)
        if matches:
            value_str = matches[0].replace(',', '')
            value = float(value_str)
            if 0 <= value <= 20:  # 利率合理范围
                return value
    except Exception:
        pass
    return None


def extract_rate_from_results(results: list, pattern: str) -> float:
    """从搜索结果中提取利率"""
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
                    if 0 <= value <= 20:
                        return value
                except:
                    continue
    return None


def save_to_database(rate_data: dict, answer: str):
    """保存利率数据到数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    current_date = datetime.now().strftime('%Y-%m-%d')
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
        INSERT INTO interest_rates
        (country_code, country_name, rate, unit, source, timestamp, date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        rate_data['code'],
        rate_data['name'],
        rate_data['rate'],
        rate_data['unit'],
        'Tavily AI',
        current_timestamp,
        current_date
    ))

    conn.commit()
    conn.close()


def get_interest_rate(code: str, config: dict) -> dict:
    """获取单个国家的利率"""
    print(f"  获取 {config['flag']} {config['name']}...")

    response = get_tavily_answer(config['query'])

    if not response['success']:
        return {
            'code': code,
            'name': config['name'],
            'flag': config['flag'],
            'success': False,
            'error': response.get('error', '查询失败')
        }

    answer = response['answer']
    print(f"    答案: {answer[:100]}...")

    rate = extract_rate_from_answer(answer, config['pattern'])

    if rate is None:
        results = response.get('results', [])
        rate = extract_rate_from_results(results, config['pattern'])

    if rate is not None:
        print(f"    ✓ 成功: {rate}%")

        # 保存到数据库
        rate_data = {
            'code': code,
            'name': config['name'],
            'rate': rate,
            'unit': '%'
        }
        save_to_database(rate_data, answer)

        return {
            'code': code,
            'name': config['name'],
            'flag': config['flag'],
            'rate': rate,
            'unit': '%',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'answer': answer,
            'success': True
        }
    else:
        print(f"    ✗ 无法提取利率")
        return {
            'code': code,
            'name': config['name'],
            'flag': config['flag'],
            'success': False,
            'error': '无法提取利率',
            'answer': answer
        }


def get_country_configs():
    """从数据库获取国家配置"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT country_code, country_name, flag, query, pattern, unit
        FROM country_config
        ORDER BY country_code
    ''')

    configs = {}
    for row in cursor.fetchall():
        code, name, flag, query, pattern, unit = row
        configs[code] = {
            'name': name,
            'flag': flag,
            'query': query,
            'pattern': pattern,
            'unit': unit
        }

    conn.close()
    return configs


def main():
    """主函数"""
    results = {
        'timestamp': datetime.now().isoformat(),
        'data': {}
    }

    print("="*80)
    print("全球货币市场利率（保存到数据库）")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # 从数据库获取配置
    configs = get_country_configs()

    # 获取所有数据
    for code, config in configs.items():
        data = get_interest_rate(code, config)
        results['data'][code] = data
        print()

    # 打印结果
    print("="*80)
    print("数据汇总")
    print("="*80)

    success_rates = []
    for code, data in results['data'].items():
        if data['success']:
            success_rates.append((data['rate'], data['flag'], data['name']))
            print(f"  {data['flag']} {data['name']}: {data['rate']}%")
        else:
            print(f"  {data['flag']} {data['name']}: {data.get('error', '失败')}")

    # 按利率排序
    success_rates.sort(reverse=True, key=lambda x: x[0])

    # 生成报告
    message = f"""🌍 全球货币市场利率报告
━━━━━━━━━━━━━━━━━━
🕐 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📡 数据源: Tavily AI 搜索

【利率数据】
"""

    # 按字母顺序显示
    order = ['CN', 'US', 'EU', 'JP', 'CA', 'AU']
    for code in order:
        if code in results['data'] and results['data'][code]['success']:
            data = results['data'][code]
            message += f"{data['flag']} {data['name']}: {data['rate']}%\n"
        elif code in results['data']:
            data = results['data'][code]
            message += f"{data['flag']} {data['name']}: {data.get('error', '失败')}\n"

    # 排名
    if success_rates:
        message += "\n【利率排名】\n"
        for i, (rate, flag, name) in enumerate(success_rates, 1):
            message += f"{i}. {flag} {name} {rate}%"
            if i == 1:
                message += " 🥇"
            elif i == 2:
                message += " 🥈"
            elif i == 3:
                message += " 🥉"
            message += "\n"

    message += "\n💡 数据已保存到数据库"
    message += "\n━━━━━━━━━━━━━━━━━━"

    # 保存完整结果
    output_file = '/home/admin/.openclaw/workspace/data/global_interest_rates.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 保存通知消息
    notify_file = '/home/admin/.openclaw/workspace/data/qq_interest_rates_notify.json'
    notify_data = {
        'timestamp': datetime.now().isoformat(),
        'message': message,
        'results': results
    }
    with open(notify_file, 'w', encoding='utf-8') as f:
        json.dump(notify_data, f, ensure_ascii=False, indent=2)

    print(f"\n完整数据: {output_file}")
    print(f"QQ通知: {notify_file}")
    print(f"数据库: {DB_PATH}")

    print("\n📱 消息预览:")
    print("-" * 80)
    print(message)
    print("-" * 80)


if __name__ == '__main__':
    main()