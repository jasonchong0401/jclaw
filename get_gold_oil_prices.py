#!/usr/bin/env python3
"""
获取黄金和石油价格
使用 Twelve Data API（你已有 API Key）
"""

from twelvedata import TDClient
import json
from datetime import datetime

# API 配置
API_KEY = "7420db1f72684a8893044c4f4ae54fc5"

# 初始化客户端
td = TDClient(apikey=API_KEY)

def get_price(symbol, name):
    """获取单个商品价格"""
    try:
        ts = td.time_series(symbol=symbol, interval='1day', outputsize=1).as_json()
        if ts and len(ts) > 0:
            latest = ts[0]
            return {
                'name': name,
                'symbol': symbol,
                'price': float(latest.get('close', 0)),
                'high': float(latest.get('high', 0)),
                'low': float(latest.get('low', 0)),
                'volume': float(latest.get('volume', 0)),
                'timestamp': latest.get('datetime', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            }
        else:
            return None
    except Exception as e:
        print(f"获取 {symbol} 失败: {e}")
        return None

def main():
    """主函数：获取黄金和石油价格"""
    results = {}

    print("=" * 70)
    print("🥇 黄金和石油价格查询")
    print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # 要查询的商品
    commodities = [
        ('XAU/USD', '黄金 (Gold)'),
        ('XAG/USD', '白银 (Silver)'),
        ('CL/USD', 'WTI 原油'),
        ('BZ/USD', '布伦特原油 (Brent Oil)'),
        ('NG/USD', '天然气 (Natural Gas)'),
    ]

    print("\n正在获取数据...")
    print("-" * 70)

    for symbol, name in commodities:
        print(f"  正在获取 {name} ({symbol})...", end=" ")
        data = get_price(symbol, name)
        if data:
            results[symbol] = data
            print(f"✅")
        else:
            print(f"❌ (可能需要更高级别套餐)")
        # 短暂延迟避免超过 API 限制
        import time
        time.sleep(1)

    print("\n" + "=" * 70)
    print("📊 价格汇总")
    print("=" * 70)

    for symbol, data in results.items():
        print(f"\n💰 {data['name']}")
        print(f"   代码: {symbol}")
        print(f"   收盘价: {data['price']:.2f}")
        print(f"   最高价: {data['high']:.2f}")
        print(f"   最低价: {data['low']:.2f}")
        if data['volume'] > 0:
            print(f"   成交量: {data['volume']:,.0f}")
        print(f"   时间: {data['timestamp']}")

    # 保存到 JSON
    output = {
        'timestamp': datetime.now().isoformat(),
        'commodities': results
    }

    output_file = '/home/admin/.openclaw/workspace/commodity_prices.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 数据已保存到: {output_file}")
    print("=" * 70)

if __name__ == '__main__':
    main()