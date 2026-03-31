#!/usr/bin/env python3
"""
获取美联储数据（负债端和资产端）
使用 Tavily API 搜索
"""

import json
import re
import subprocess
from datetime import datetime

# Tavily 脚本路径
TAVILY_SCRIPT = "/home/admin/.openclaw/workspace/skills/tavily-search/skill/scripts/tavily_search.py"

# 美联储数据配置
FED_DATA = {
    # 负债端
    'TGA': {
        'name': 'TGA账户余额（财政部一般账户）',
        'query': 'What is the current US Treasury General Account TGA balance?',
        'pattern': r'([\$]?\s*[0-9,]+\.?[0-9]*)\s*(?:billion|trillion)\s*(?:USD)?',
        'unit': 'billion USD',
        'decimal': 2
    },
    'EXCESS_RESERVES': {
        'name': '超额储备余额',
        'query': 'What is the current excess reserves balance at Federal Reserve?',
        'pattern': r'([\$]?\s*[0-9,]+\.?[0-9]*)\s*(?:billion|trillion)\s*(?:USD)?',
        'unit': 'billion USD',
        'decimal': 2
    },
    'RRP': {
        'name': '隔夜逆回购账户余额',
        'query': 'What is the current Federal Reserve overnight reverse repurchase facility RRP balance?',
        'pattern': r'([\$]?\s*[0-9,]+\.?[0-9]*)\s*(?:billion|trillion)\s*(?:USD)?',
        'unit': 'billion USD',
        'decimal': 2
    },
    # 资产端
    'MBS': {
        'name': 'MBS持有量（抵押贷款支持证券）',
        'query': 'What is the current Federal Reserve holdings of mortgage-backed securities MBS?',
        'pattern': r'([\$]?\s*[0-9,]+\.?[0-9]*)\s*(?:billion|trillion)\s*(?:USD)?',
        'unit': 'billion USD',
        'decimal': 2
    },
    'TREASURY_10Y': {
        'name': '10年期国债持仓量',
        'query': 'What is the current Federal Reserve holdings of 10-year treasury securities?',
        'pattern': r'([\$]?\s*[0-9,]+\.?[0-9]*)\s*(?:billion|trillion)\s*(?:USD)?',
        'unit': 'billion USD',
        'decimal': 2
    },
    'TREASURY_2Y': {
        'name': '2年期国债持仓量',
        'query': 'What is the current Federal Reserve holdings of 2-year treasury securities?',
        'pattern': r'([\$]?\s*[0-9,]+\.?[0-9]*)\s*(?:billion|trillion)\s*(?:USD)?',
        'unit': 'billion USD',
        'decimal': 2
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


def extract_value_from_answer(answer: str) -> float:
    """从答案中提取数值"""
    if not answer:
        return None

    try:
        # 清理答案文本
        cleaned = re.sub(r'[^\x00-\x7F]+', '', answer)

        # 查找数值（可能是billion或trillion）
        # 格式: $X billion 或 X trillion
        patterns = [
            r'[\$]?\s*([0-9,]+\.?[0-9]*)\s*billion',
            r'[\$]?\s*([0-9,]+\.?[0-9]*)\s*trillion'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, cleaned, re.IGNORECASE)
            if matches:
                value_str = matches[0].replace(',', '')
                value = float(value_str)

                # 如果是trillion，转换为billion
                if 'trillion' in cleaned.lower():
                    value *= 1000

                if 0 < value < 100000:
                    return value
    except Exception as e:
        print(f"    提取失败: {e}")
        return None

    return None


def extract_value_from_results(results: list) -> float:
    """从搜索结果中提取数值"""
    if not results:
        return None

    for result in results:
        content = result.get('content', '')
        if content:
            patterns = [
                r'[\$]?\s*([0-9,]+\.?[0-9]*)\s*billion',
                r'[\$]?\s*([0-9,]+\.?[0-9]*)\s*trillion'
            ]

            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    try:
                        value_str = matches[0].replace(',', '')
                        value = float(value_str)

                        if 'trillion' in content.lower():
                            value *= 1000

                        if 0 < value < 100000:
                            return value
                    except:
                        continue

    return None


def get_fed_data(key: str, config: dict) -> dict:
    """获取单个美联储数据"""
    print(f"  获取 {config['name']} ({key})...")
    print(f"    查询: {config['query']}")

    # 获取 Tavily 答案
    response = get_tavily_answer(config['query'])

    if not response['success']:
        print(f"    ✗ 查询失败: {response.get('error', 'Unknown error')}")
        return {
            'key': key,
            'name': config['name'],
            'success': False,
            'error': response.get('error', '查询失败')
        }

    # 尝试从答案中提取
    answer = response['answer']
    print(f"    答案: {answer[:100]}...")

    value = extract_value_from_answer(answer)

    # 如果答案中没有，尝试从搜索结果中提取
    if value is None:
        results = response.get('results', [])
        value = extract_value_from_results(results)

    if value:
        print(f"    ✓ 成功: {value:.{config['decimal']}f} {config['unit']}")
        return {
            'key': key,
            'name': config['name'],
            'value': value,
            'unit': config['unit'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'answer': answer,
            'success': True
        }
    else:
        print(f"    ✗ 无法提取数值")
        return {
            'key': key,
            'name': config['name'],
            'success': False,
            'error': '无法提取数值',
            'answer': answer
        }


def main():
    """主函数"""
    results = {
        'timestamp': datetime.now().isoformat(),
        'data': {}
    }

    print("="*80)
    print("获取美联储数据（使用 Tavily AI）")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # 获取所有数据
    for key, config in FED_DATA.items():
        data = get_fed_data(key, config)
        results['data'][key] = data
        print()  # 空行分隔

    # 打印结果
    print("="*80)
    print("数据汇总")
    print("="*80)

    success_count = 0
    failed_count = 0

    for key, data in results['data'].items():
        if data['success']:
            success_count += 1
            value = data['value']
            unit = data['unit']
            decimal = FED_DATA[key]['decimal']
            print(f"  ✓ {data['name']}: {value:.{decimal}f} {unit}")
        else:
            failed_count += 1
            print(f"  ✗ {data['name']}: {data.get('error', '失败')}")

    # 保存完整结果
    output_file = '/home/admin/.openclaw/workspace/data/fed_data_tavily.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 生成通知消息
    message = f"""【美联储数据】
"""

    for key, data in results['data'].items():
        if data['success']:
            value = data['value']
            unit = data['unit']
            decimal = FED_DATA[key]['decimal']
            message += f"✓ {data['name']}: {value:.{decimal}f} {unit}\n"
        else:
            message += f"✗ {data['name']}: {data.get('error', '失败')}\n"

    if success_count > 0:
        message += f"\n✅ 成功获取: {success_count} 项"
    if failed_count > 0:
        message += f"\n❌ 失败: {failed_count} 项"

    # 保存通知消息
    notify_file = '/home/admin/.openclaw/workspace/data/qq_fed_notify.json'
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