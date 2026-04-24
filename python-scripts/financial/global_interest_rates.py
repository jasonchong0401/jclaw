#!/usr/bin/env python3
"""
获取全球主要国家货币市场利率并保存到数据库
使用 Tavily API 获取实时利率数据
支持与前一日的对比和变化百分比
"""

import json
import re
import subprocess
import sqlite3
from datetime import datetime, timedelta

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


def get_previous_rates(date: datetime) -> dict:
    """获取指定日期的利率数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    date_str = date.strftime('%Y-%m-%d')

    cursor.execute('''
        SELECT country_code, rate
        FROM interest_rates
        WHERE date = ?
    ''', (date_str,))

    rates = {}
    for row in cursor.fetchall():
        code, rate = row
        rates[code] = rate

    conn.close()
    return rates


def calculate_change(current: float, previous: float) -> dict:
    """计算变化百分比"""
    if previous is None or previous == 0:
        return {
            'absolute': None,
            'percentage': None,
            'direction': None
        }

    absolute = current - previous
    percentage = (absolute / previous) * 100

    direction = 'neutral'
    if absolute > 0:
        direction = 'up'
    elif absolute < 0:
        direction = 'down'

    return {
        'absolute': absolute,
        'percentage': percentage,
        'direction': direction
    }


def format_change(change: dict, decimal: int = 2) -> str:
    """格式化变化显示"""
    if change['percentage'] is None:
        return ""

    emoji = {
        'up': '📈',
        'down': '📉',
        'neutral': '➡️'
    }

    direction = change['direction']
    percentage = change['percentage']

    # 如果变化很小（< 0.01%），显示"无变化"
    if abs(percentage) < 0.01:
        return "➡️ 无变化"

    # 根据变化大小调整小数位数
    if abs(percentage) >= 100:
        adjusted_decimal = 1
    elif abs(percentage) >= 10:
        adjusted_decimal = 2
    else:
        adjusted_decimal = 3

    sign = '+' if percentage > 0 else ''
    return f"{emoji[direction]} {sign}{percentage:.{adjusted_decimal}f}%"


def compare_with_previous(current_data: dict, previous_data: dict) -> dict:
    """对比当前数据和前一天数据"""
    comparison = {}

    for code, current in current_data.items():
        if not current['success']:
            comparison[code] = {
                'code': code,
                'name': current['name'],
                'flag': current['flag'],
                'current': None,
                'previous': None,
                'change': None,
                'success': False
            }
            continue

        prev_rate = previous_data.get(code)

        if prev_rate is not None:
            curr_rate = current['rate']
            change = calculate_change(curr_rate, prev_rate)

            comparison[code] = {
                'code': code,
                'name': current['name'],
                'flag': current['flag'],
                'current': curr_rate,
                'previous': prev_rate,
                'change': change,
                'unit': current['unit'],
                'success': True
            }
        else:
            comparison[code] = {
                'code': code,
                'name': current['name'],
                'flag': current['flag'],
                'current': current['rate'],
                'previous': None,
                'change': None,
                'unit': current['unit'],
                'success': True
            }

    return comparison


def main():
    """主函数"""
    current_date = datetime.now()
    previous_date = current_date - timedelta(days=1)

    results = {
        'timestamp': current_date.isoformat(),
        'date': current_date.strftime('%Y-%m-%d'),
        'data': {}
    }

    print("="*80)
    print("全球货币市场利率（保存到数据库）")
    print(f"时间: {current_date.strftime('%Y-%m-%d %H:%M:%S')}")
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

    # 加载前一天的利率数据
    print("\n" + "="*80)
    print("加载历史数据")
    print("="*80)
    previous_rates = get_previous_rates(previous_date)
    if previous_rates:
        print(f"  ✓ 加载 {previous_date.strftime('%Y-%m-%d')} 的历史数据")
    else:
        print(f"  未找到 {previous_date.strftime('%Y-%m-%d')} 的历史数据")

    # 对比数据
    comparison = compare_with_previous(results['data'], previous_rates)

    # 打印对比结果
    if comparison:
        print("\n" + "="*80)
        print("数据对比（今日 vs 昨日）")
        print("="*80)

        for code, comp in comparison.items():
            if comp['success'] and comp['change'] and comp['change']['percentage'] is not None:
                prev = comp['previous']
                curr = comp['current']
                change = comp['change']
                change_str = format_change(change, 3)
                print(f"  {comp['flag']} {comp['name']}: {prev:.2f}% → {curr:.2f}% {change_str}")
            elif comp['success']:
                print(f"  {comp['flag']} {comp['name']}: {comp['current']:.2f}% (无昨日数据)")

    # 按利率排序
    success_rates.sort(reverse=True, key=lambda x: x[0])

    # 生成报告（改进格式）
    message = f"""🌍 全球货币市场利率报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 更新时间: {current_date.strftime('%Y-%m-%d %H:%M:%S')}
📡 数据源:   Tavily AI 搜索

【今日利率 vs 昨日】
"""

    # 按固定顺序显示，加上对比
    order = ['CN', 'US', 'EU', 'JP', 'CA', 'AU']
    for code in order:
        if code in comparison and comparison[code]['success']:
            comp = comparison[code]
            curr = comp['current']

            # 计算最长名称用于对齐
            name_with_flag = f"{comp['flag']} {comp['name']}"
            rate_str = f"{curr:.2f}%"

            # 添加变化
            if comp['change'] and comp['change']['percentage'] is not None:
                change_str = format_change(comp['change'], 3)
                message += f"{name_with_flag:20s} {rate_str:>8s}  {change_str}\n"
            else:
                message += f"{name_with_flag:20s} {rate_str:>8s}  (无昨日数据)\n"
        elif code in results['data']:
            data = results['data'][code]
            message += f"{data['flag']} {data['name']:15s}: 获取失败\n"

    # 排名（改进格式）
    if success_rates:
        message += "\n【利率排名】\n"
        for i, (rate, flag, name) in enumerate(success_rates, 1):
            rank_str = f"{i}."
            name_str = f"{flag} {name}"
            rate_str = f"{rate:.2f}%"

            medal = ""
            if i == 1:
                medal = " 🥇"
            elif i == 2:
                medal = " 🥈"
            elif i == 3:
                medal = " 🥉"

            message += f"{rank_str} {name_str:15s} {rate_str:>8s}{medal}\n"

    message += "\n💡 数据已保存到数据库"
    message += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # 保存完整结果
    output_file = '/home/admin/.openclaw/workspace/data/global_interest_rates.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 保存通知消息
    notify_file = '/home/admin/.openclaw/workspace/data/qq_interest_rates_notify.json'
    notify_data = {
        'timestamp': current_date.isoformat(),
        'date': current_date.strftime('%Y-%m-%d'),
        'message': message,
        'results': results,
        'comparison': comparison
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