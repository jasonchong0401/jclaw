#!/usr/bin/env python3
"""
获取金融数据脚本 (优化版)
使用 Twelve Data API 获取各类金融指标的最新数据
使用批量请求减少API调用次数
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

# 初始化客户端
td = TDClient(apikey=API_KEY)


def get_batch_time_series(symbols, interval='1day', outputsize=1):
    """批量获取时间序列数据"""
    try:
        # 使用批量请求
        ts = td.time_series(symbol=symbols, interval=interval, outputsize=outputsize).as_json()
        return ts
    except Exception as e:
        print(f"批量获取失败: {e}")
        return None


def get_single_time_series(symbol, interval='1day', outputsize=1):
    """单个获取时间序列数据"""
    try:
        ts = td.time_series(symbol=symbol, interval=interval, outputsize=outputsize).as_json()
        if ts and len(ts) > 0:
            latest = ts[0]
            return {
                'price': float(latest.get('close', 0)),
                'timestamp': latest.get('datetime', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            }
        return None
    except Exception as e:
        print(f"获取 {symbol} 失败: {e}")
        return None


def main():
    """主函数：获取所有需要的金融数据"""
    results = {}

    print("="*80)
    print("开始获取金融数据")
    print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # 第一批：市场数据（批量请求）
    print("\n[1/3] 获取市场数据...")
    market_symbols = [
        ('US10Y', '美国十年期国债利率'),
        ('US2Y', '2年期美国国债'),
        ('US5Y', '5年期美国国债'),
        ('US30Y', '30年期美国国债'),
        ('VIX', 'VIX恐慌指数'),
        ('XAU/USD', '黄金价格'),
        ('XAG/USD', '白银价格'),
        ('CL/USD', '原油期货价格'),
        ('SOFR/USD', 'SOFR利率')
    ]

    market_batch = {}
    for symbol, name in market_symbols:
        print(f"  - {name} ({symbol})...")
        data = get_single_time_series(symbol)
        if data:
            market_batch[symbol] = {
                'name': name,
                **data
            }
        time.sleep(1)  # 避免超过配额

    results['market'] = market_batch

    # 第二批：等待后获取美联储负债端数据
    print("\n[2/3] 获取美联储负债端数据...")
    print("等待 60 秒以重置 API 配额...")
    time.sleep(60)

    fed_liability_symbols = [
        ('RRPONTSYD', '隔夜逆回购余额'),
        # 注意：TGA和IORB可能需要更高级别套餐
    ]

    for symbol, name in fed_liability_symbols:
        print(f"  - {name} ({symbol})...")
        data = get_single_time_series(symbol)
        if data:
            results[symbol] = {
                'name': name,
                **data
            }
        time.sleep(1)

    # 第三批：美联储资产端数据
    print("\n[3/3] 获取美联储资产端数据...")
    print("等待 60 秒以重置 API 配额...")
    time.sleep(60)

    fed_asset_symbols = [
        # MBS 等美联储持仓数据可能需要特定符号或更高级别套餐
    ]

    # 打印结果
    print("\n" + "="*80)
    print("金融数据汇总")
    print("="*80)
    print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 市场数据
    print("【市场数据】")
    for symbol, data in results.get('market', {}).items():
        if 'price' in data:
            if '利率' in data['name'] or 'VIX' in data['name']:
                print(f"  {data['name']}: {data['price']:.4f}%")
            else:
                print(f"  {data['name']}: {data['price']:.4f}")
        else:
            print(f"  {data['name']}: 未获取到数据")

    # 美联储数据
    print("\n【美联储数据】")
    for symbol, data in results.items():
        if symbol != 'market':
            if 'price' in data:
                print(f"  {data['name']}: {data['price']:,.2f}")
            else:
                print(f"  {data.get('name', symbol)}: 未获取到数据")

    # 保存完整结果到JSON
    output_file = '/home/admin/.openclaw/workspace/data/financial_data.json'
    summary = {
        'timestamp': datetime.now().isoformat(),
        'data': results
    }
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\n完整数据已保存到: {output_file}")

    # 也保存一个简化的版本
    simplified = {
        'timestamp': datetime.now().isoformat(),
        'market': {},
        'fed': {}
    }

    for symbol, data in results.get('market', {}).items():
        if 'price' in data:
            simplified['market'][symbol] = {
                'name': data['name'],
                'price': data['price'],
                'timestamp': data['timestamp']
            }

    for symbol, data in results.items():
        if symbol != 'market' and 'price' in data:
            simplified['fed'][symbol] = {
                'name': data['name'],
                'price': data['price'],
                'timestamp': data['timestamp']
            }

    summary_file = '/home/admin/.openclaw/workspace/data/financial_data_summary.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(simplified, f, ensure_ascii=False, indent=2)
    print(f"摘要数据已保存到: {summary_file}")

    print("\n" + "="*80)
    print("提示:")
    print("- 部分数据（如白银、原油、TGA、MBS等）可能需要更高级别的 API 套餐")
    print("- 免费版本每分钟限制 8 次 API 调用")
    print("- 建议升级到付费套餐以获取完整数据")
    print("="*80)


if __name__ == '__main__':
    main()