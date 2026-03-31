#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
黄金和石油价格爬取脚本（备选版本）
使用 requests + BeautifulSoup 从 Kitco 获取价格
"""

import requests
from bs4 import BeautifulSoup
import json
import datetime
import time

def get_headers():
    """获取请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

def get_kitco_prices():
    """从 Kitco 获取贵金属价格"""
    url = "https://www.kitco.com/price/precious-metals"

    print(f"正在从 Kitco 获取价格...")
    response = requests.get(url, headers=get_headers(), timeout=30)

    if response.status_code != 200:
        print(f"❌ 请求失败: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []

    # Kitco 的价格通常在表格中
    # 查找包含价格的表格行
    tables = soup.find_all('table')
    print(f"找到 {len(tables)} 个表格")

    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 3:
                commodity = cells[0].get_text(strip=True)
                if any(x in commodity.lower() for x in ['gold', 'silver', 'platinum', 'palladium']):
                    price = cells[1].get_text(strip=True) if len(cells) > 1 else 'N/A'
                    change = cells[2].get_text(strip=True) if len(cells) > 2 else 'N/A'

                    results.append({
                        "commodity": commodity,
                        "price": price,
                        "change": change
                    })

    return results

def get_yahoo_finance_price(symbol, name):
    """从 Yahoo Finance 获取价格（备选）"""
    url = f"https://finance.yahoo.com/quote/{symbol}"

    try:
        response = requests.get(url, headers=get_headers(), timeout=30)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Yahoo 的价格通常在特定元素中
        price_elem = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
        change_elem = soup.find('fin-streamer', {'data-field': 'regularMarketChangePercent'})

        if price_elem:
            return {
                "commodity": name,
                "symbol": symbol,
                "price": price_elem.get_text(strip=True),
                "percent_change": change_elem.get_text(strip=True) if change_elem else 'N/A',
                "source": "Yahoo Finance"
            }
    except Exception as e:
        print(f"获取 {symbol} 时出错: {e}")

    return None

def main():
    print("=" * 60)
    print("📊 商品价格查询")
    print("=" * 60)

    # 方法 1: 尝试从 Kitco 获取
    kitco_results = get_kitco_prices()

    if kitco_results:
        print("\n" + "=" * 60)
        print("💰 Kitco 贵金属价格")
        print("=" * 60)

        for item in kitco_results:
            print(f"\n{item['commodity']}")
            print(f"价格: {item['price']}")
            print(f"涨跌: {item['change']}")
    else:
        print("\n❌ 无法从 Kitco 获取数据")

    # 方法 2: 尝试从 Yahoo Finance 获取
    print("\n" + "=" * 60)
    print("📈 Yahoo Finance 价格")
    print("=" * 60)

    symbols = {
        'GC=F': 'Gold Futures',
        'SI=F': 'Silver Futures',
        'CL=F': 'Crude Oil WTI',
        'BZ=F': 'Brent Oil',
    }

    yahoo_results = []
    for symbol, name in symbols.items():
        print(f"正在获取 {name}...")
        result = get_yahoo_finance_price(symbol, name)
        if result:
            yahoo_results.append(result)
            print(f"✅ {name}: {result['price']} ({result['percent_change']})")
            time.sleep(1)  # 避免请求过快
        else:
            print(f"❌ 无法获取 {name}")

    # 保存结果
    data = {
        "fetched_at": datetime.datetime.now().isoformat(),
        "kitco_prices": kitco_results,
        "yahoo_prices": yahoo_results
    }

    output_file = 'commodity_prices.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 数据已保存到 {output_file}")

if __name__ == "__main__":
    main()