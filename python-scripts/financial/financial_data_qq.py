#!/usr/bin/env python3
"""
获取金融数据并通过 QQ 通知
"""

from twelvedata import TDClient
import json
from datetime import datetime
import time
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API 配置
API_KEY = os.getenv('TWELVEDATA_API_KEY')
if not API_KEY:
    raise ValueError("未找到 TWELVEDATA_API_KEY 环境变量，请在 .env 文件中配置")
td = TDClient(apikey=API_KEY)

# 输出文件
OUTPUT_FILE = '/home/admin/.openclaw/workspace/data/financial_data.json'
QQ_NOTIFY_FILE = '/home/admin/.openclaw/workspace/data/qq_notify.json'


def get_data(symbol, name, delay=0):
    """获取单个数据点"""
    if delay > 0:
        time.sleep(delay)
    try:
        # 先尝试 quote 端点
        result = td.quote(symbol=symbol).as_json()
        if result and 'close' in result:
            return {
                'name': name,
                'symbol': symbol,
                'price': float(result['close']),
                'timestamp': result.get('datetime', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                'success': True
            }
        else:
            # 尝试 time_series
            ts = td.time_series(symbol=symbol, interval='1day', outputsize=1).as_json()
            if ts and len(ts) > 0 and 'close' in ts[0]:
                return {
                    'name': name,
                    'symbol': symbol,
                    'price': float(ts[0]['close']),
                    'timestamp': ts[0].get('datetime', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                    'success': True
                }
            return {'name': name, 'symbol': symbol, 'success': False, 'error': 'No data available'}
    except Exception as e:
        error_msg = str(e)
        if 'Grow or Venture' in error_msg:
            error_msg = '需要 Grow/Venture 套餐'
        elif 'Ultra or Enterprise' in error_msg:
            error_msg = '需要 Ultra/Enterprise 套餐'
        elif 'Pro or Venture' in error_msg:
            error_msg = '需要 Pro/Venture 套餐'
        return {'name': name, 'symbol': symbol, 'success': False, 'error': error_msg}


def main():
    results = {
        'timestamp': datetime.now().isoformat(),
        'data': {}
    }

    print("="*80)
    print("开始获取金融数据")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # 可用的数据（免费套餐）
    available_data = [
        ('XAU/USD', '黄金价格', 1),
        ('SOFR', 'SOFR利率', 2),
        ('US2Y', '2年期美国国债', 3),
    ]

    # 尝试其他数据（可能需要更高套餐）
    try_other_data = [
        ('US10Y', '美国十年期国债利率', 0),
        ('XAG/USD', '白银价格', 0),
        ('VIX', 'VIX恐慌指数', 0),
        ('TGA', 'TGA账户余额', 0),
        ('IORB', '超额储备余额', 0),
        ('RRPONTSYD', '隔夜逆回购余额', 0),
    ]

    # 先获取可用的数据
    print("\n【获取可用数据】")
    for symbol, name, delay in available_data:
        print(f"  获取 {name}...")
        data = get_data(symbol, name, delay)
        results['data'][symbol] = data
        if data['success']:
            print(f"    ✓ {name}: {data['price']}")
        else:
            print(f"    ✗ {name}: {data.get('error', '失败')}")

    # 尝试其他数据
    print("\n【尝试获取其他数据】")
    for symbol, name, delay in try_other_data:
        print(f"  获取 {name}...")
        data = get_data(symbol, name, delay)
        results['data'][symbol] = data
        if data['success']:
            print(f"    ✓ {name}: {data['price']}")
        else:
            print(f"    ✗ {name}: {data.get('error', '失败')}")

    # 保存完整结果
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 生成 QQ 通知消息
    message = f"""📊 金融数据报告
━━━━━━━━━━━━━━━━━━
🕐 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

【市场数据】
"""

    # 添加成功获取的数据
    success_count = 0
    for symbol, data in results['data'].items():
        if data['success']:
            success_count += 1
            value = data['price']
            if '利率' in data['name'] or '国债' in data['name']:
                message += f"✓ {data['name']}: {value:.4f}%\n"
            else:
                message += f"✓ {data['name']}: {value:.2f}\n"

    if success_count == 0:
        message += "⚠️ 暂无可用数据\n"

    # 添加失败的数据说明
    failed_items = [(k, v) for k, v in results['data'].items() if not v['success']]
    if failed_items:
        message += "\n【说明】\n"
        for symbol, data in failed_items:
            message += f"✗ {data['name']}: {data.get('error', '获取失败')}\n"

    message += "\n💡 提示:\n"
    message += "- 白银、原油、VIX等数据需要 Grow/Venture 套餐\n"
    message += "- 美联储资产负债表数据需要 Pro/Venture 套餐\n"
    message += f"- 当前套餐: 免费版 (8次/分钟)\n"
    message += "━━━━━━━━━━━━━━━━━━"

    # 保存 QQ 通知消息
    notify_data = {
        'timestamp': datetime.now().isoformat(),
        'message': message,
        'results': results
    }
    with open(QQ_NOTIFY_FILE, 'w', encoding='utf-8') as f:
        json.dump(notify_data, f, ensure_ascii=False, indent=2)

    print("\n" + "="*80)
    print("获取完成")
    print(f"成功: {success_count} 项")
    print(f"失败: {len(failed_items)} 项")
    print(f"数据文件: {OUTPUT_FILE}")
    print(f"QQ通知文件: {QQ_NOTIFY_FILE}")
    print("="*80)

    # 打印消息预览
    print("\n📱 QQ 通知消息预览:")
    print("-" * 80)
    print(message)
    print("-" * 80)


if __name__ == '__main__':
    main()