#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
黄金和石油价格爬取脚本
使用 Scrapling 框架从 investing.com 获取实时价格
"""

from scrapling.fetchers import StealthyFetcher
import json
import datetime

# 启用自适应模式（网站改版后仍能工作）
StealthyFetcher.adaptive = True

def get_gold_price():
    """获取黄金价格"""
    url = "https://www.investing.com/commodities/gold"

    print(f"正在获取黄金价格...")
    page = StealthyFetcher.fetch(
        url,
        headless=True,
        network_idle=True
    )

    # 提取价格（使用自适应选择器）
    price_element = page.css('[data-test="instrument-price-last"]', adaptive=True)

    if price_element:
        price = price_element.text().get()
        change = page.css('[data-test="instrument-price-change"]').text().get()
        percent = page.css('[data-test="instrument-price-percent-change"]').text().get()
        timestamp = page.css('[data-test="instrument-time"]').text().get()

        return {
            "commodity": "Gold (XAU/USD)",
            "price": price,
            "change": change,
            "percent_change": percent,
            "timestamp": timestamp
        }
    return None

def get_oil_prices():
    """获取石油期货价格"""
    results = []

    # WTI 原油
    print(f"正在获取 WTI 原油价格...")
    wti_url = "https://www.investing.com/commodities/crude-oil-wti"
    page = StealthyFetcher.fetch(wti_url, headless=True)

    price = page.css('[data-test="instrument-price-last"]', adaptive=True)
    if price:
        results.append({
            "commodity": "WTI Crude Oil",
            "price": price.text().get(),
            "change": page.css('[data-test="instrument-price-change"]').text().get(),
            "percent_change": page.css('[data-test="instrument-price-percent-change"]').text().get()
        })

    # 布伦特原油
    print(f"正在获取布伦特原油价格...")
    brent_url = "https://www.investing.com/commodities/brent-oil"
    page = StealthyFetcher.fetch(brent_url, headless=True)

    price = page.css('[data-test="instrument-price-last"]', adaptive=True)
    if price:
        results.append({
            "commodity": "Brent Crude Oil",
            "price": price.text().get(),
            "change": page.css('[data-test="instrument-price-change"]').text().get(),
            "percent_change": page.css('[data-test="instrument-price-percent-change"]').text().get()
        })

    return results

def main():
    print("=" * 60)
    print("🥇 黄金价格")
    print("=" * 60)

    gold = get_gold_price()
    if gold:
        print(f"价格: {gold['price']}")
        print(f"涨跌: {gold['change']} ({gold['percent_change']})")
        print(f"时间: {gold.get('timestamp', 'N/A')}")
    else:
        print("❌ 无法获取黄金价格")

    print("\n" + "=" * 60)
    print("🛢️ 石油期货价格")
    print("=" * 60)

    oils = get_oil_prices()
    for oil in oils:
        print(f"\n{oil['commodity']}")
        print(f"价格: {oil['price']}")
        print(f"涨跌: {oil['change']} ({oil['percent_change']})")

    # 保存为 JSON
    data = {
        "fetched_at": datetime.datetime.now().isoformat(),
        "gold": gold,
        "oil": oils
    }

    output_file = 'commodity_prices.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 数据已保存到 {output_file}")

if __name__ == "__main__":
    main()