#!/usr/bin/env python3
"""
获取金融数据脚本（使用 Tavily 的 include-answer 功能）
支持前后两天的数据对比和变化百分比
"""

import json
import re
import subprocess
from datetime import datetime, timedelta
import os
from pathlib import Path

# Tavily 脚本路径
TAVILY_SCRIPT = "/home/admin/.openclaw/workspace/skills/tavily-search/skill/scripts/tavily_search.py"

# 数据目录
DATA_DIR = Path("/home/admin/.openclaw/workspace/data/financial")
HISTORY_DIR = DATA_DIR / "history"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

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


def get_tavily_answer(query: str, max_retries: int = 3) -> dict:
    """使用 Tavily 获取答案（带重试）"""
    for attempt in range(max_retries):
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
                    if attempt < max_retries - 1:
                        print(f"    重试 {attempt + 1}/{max_retries}...")
                        import time
                        time.sleep(2)
                        continue
                    return {'success': False, 'error': 'Invalid JSON'}
            else:
                if attempt < max_retries - 1:
                    print(f"    请求失败，重试 {attempt + 1}/{max_retries}...")
                    import time
                    time.sleep(2)
                    continue
                return {'success': False, 'error': 'Tavily request failed'}
        except subprocess.TimeoutExpired:
            if attempt < max_retries - 1:
                print(f"    超时，重试 {attempt + 1}/{max_retries}...")
                import time
                time.sleep(3)
                continue
            return {'success': False, 'error': 'Timeout'}
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"    异常: {e}，重试 {attempt + 1}/{max_retries}...")
                import time
                time.sleep(2)
                continue
            return {'success': False, 'error': str(e)}

    return {'success': False, 'error': 'Max retries exceeded'}


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

            # 清理末尾的小数点和其他非数字字符
            value_str = re.sub(r'[^\d.]$', '', value_str)  # 移除末尾的非数字字符
            value_str = re.sub(r'\.$', '', value_str)  # 移除末尾的小数点
            value_str = re.sub(r'^\.', '', value_str)  # 移除开头的小数点

            # 确保只有一个小数点
            if value_str.count('.') > 1:
                parts = value_str.split('.')
                value_str = parts[0] + '.' + ''.join(parts[1:])

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
            print(f"    ✓ 从搜索结果提取成功: {price:.{config['decimal']}f}{config['unit']}")

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


def load_previous_data(date: datetime) -> dict:
    """加载指定日期的历史数据"""
    filename = f"financial_data_{date.strftime('%Y-%m-%d')}.json"
    filepath = HISTORY_DIR / filename

    if not filepath.exists():
        print(f"  未找到 {date.strftime('%Y-%m-%d')} 的历史数据")
        return {}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"  ✓ 加载 {date.strftime('%Y-%m-%d')} 的历史数据")
            return data.get('data', {})
    except Exception as e:
        print(f"  ✗ 加载历史数据失败: {e}")
        return {}


def save_current_data(date: datetime, data: dict):
    """保存当前数据到历史文件"""
    filename = f"financial_data_{date.strftime('%Y-%m-%d')}.json"
    filepath = HISTORY_DIR / filename

    output_data = {
        'date': date.strftime('%Y-%m-%d'),
        'timestamp': datetime.now().isoformat(),
        'data': data
    }

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"  ✓ 保存当前数据到 {filename}")
    except Exception as e:
        print(f"  ✗ 保存数据失败: {e}")


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
    absolute = change['absolute']

    # 格式化符号和百分比
    sign = '+' if percentage > 0 else ''
    change_str = f"{sign}{percentage:.{decimal}f}%"

    # 如果是价格类（不是百分比），显示绝对值
    if abs(percentage) < 100:  # 假设变化超过100%的可能是利率等百分比数据
        return f"{emoji[direction]} {change_str}"

    return f"{emoji[direction]} {change_str}"


def compare_with_previous(current_data: dict, previous_data: dict) -> dict:
    """对比当前数据和前一天数据"""
    comparison = {}

    for symbol, current in current_data.items():
        if not current['success']:
            comparison[symbol] = {
                'symbol': symbol,
                'name': current['name'],
                'current': None,
                'previous': None,
                'change': None,
                'success': False
            }
            continue

        prev_record = previous_data.get(symbol, {})

        if prev_record.get('success') and 'price' in prev_record:
            prev_price = prev_record['price']
            curr_price = current['price']

            change = calculate_change(curr_price, prev_price)

            comparison[symbol] = {
                'symbol': symbol,
                'name': current['name'],
                'current': curr_price,
                'previous': prev_price,
                'change': change,
                'unit': current['unit'],
                'decimal': FINANCIAL_DATA[symbol]['decimal'],
                'success': True
            }
        else:
            comparison[symbol] = {
                'symbol': symbol,
                'name': current['name'],
                'current': current['price'],
                'previous': None,
                'change': None,
                'unit': current['unit'],
                'decimal': FINANCIAL_DATA[symbol]['decimal'],
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
    print("获取金融数据（使用 Tavily AI）")
    print(f"时间: {current_date.strftime('%Y-%m-%d %H:%M:%S')}")
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

    # 保存当前数据到历史文件
    save_current_data(current_date, results['data'])

    # 加载前一天的数据
    print("\n" + "="*80)
    print("加载历史数据")
    print("="*80)
    previous_data = load_previous_data(previous_date)

    # 对比数据
    comparison = compare_with_previous(results['data'], previous_data)

    # 打印对比结果
    if comparison:
        print("\n" + "="*80)
        print("数据对比（今日 vs 昨日）")
        print("="*80)

        for symbol, comp in comparison.items():
            if comp['success'] and comp['change'] and comp['change']['percentage'] is not None:
                current = comp['current']
                previous = comp['previous']
                change = comp['change']
                unit = comp['unit']
                decimal = comp['decimal']

                change_str = format_change(change, decimal)
                print(f"  {comp['name']}: {previous:.{decimal}f}{unit} → {current:.{decimal}f}{unit} {change_str}")
            elif comp['success']:
                print(f"  {comp['name']}: {comp['current']:.{comp['decimal']}f}{comp['unit']} (无昨日数据)")
            else:
                print(f"  {comp['name']}: 数据获取失败")

    # 生成通知消息（带对比）
    message = f"""📊 金融数据报告
━━━━━━━━━━━━━━━━━━
🕐 更新时间: {current_date.strftime('%Y-%m-%d %H:%M:%S')}
📡 数据源: Tavily AI 搜索

【实时数据】
"""

    for symbol, comp in comparison.items():
        if comp['success']:
            current = comp['current']
            unit = comp['unit']
            decimal = comp['decimal']

            # 添加变化趋势
            if comp['change'] and comp['change']['percentage'] is not None:
                change_str = format_change(comp['change'], decimal)
                message += f"{comp['name']}: {current:.{decimal}f}{unit} {change_str}\n"
            else:
                message += f"✓ {comp['name']}: {current:.{decimal}f}{unit}\n"
        else:
            message += f"✗ {comp['name']}: 获取失败\n"

    if success_count > 0:
        message += f"\n✅ 成功获取: {success_count} 项"
    if failed_count > 0:
        message += f"\n❌ 失败: {failed_count} 项"

    message += "\n━━━━━━━━━━━━━━━━━━"

    # 保存完整结果
    output_file = '/home/admin/.openclaw/workspace/data/financial_data_tavily.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 保存通知消息
    notify_file = '/home/admin/.openclaw/workspace/data/qq_financial_notify.json'
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
    print(f"历史数据目录: {HISTORY_DIR}")

    print("\n📱 消息预览:")
    print("-" * 80)
    print(message)
    print("-" * 80)

    # 如果至少有一个成功，返回0，否则返回1
    if success_count > 0:
        print(f"\n✅ 至少获取了 {success_count} 项数据，继续发送")
        return 0
    else:
        print(f"\n❌ 所有数据获取失败，跳过发送")
        return 1


if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)