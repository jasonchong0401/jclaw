#!/usr/bin/env python3
"""
测试 Twelve Data API 的符号可用性
"""

from twelvedata import TDClient
import time
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

API_KEY = os.getenv('TWELVEDATA_API_KEY')
if not API_KEY:
    raise ValueError("未找到 TWELVEDATA_API_KEY 环境变量，请在 .env 文件中配置")
td = TDClient(apikey=API_KEY)


def test_symbol(symbol, description):
    """测试单个符号"""
    try:
        result = td.quote(symbol=symbol).as_json()
        if result and 'close' in result:
            print(f"✓ {description:30} ({symbol:15}): {result['close']}")
            return True, float(result['close'])
        elif result and 'message' in result:
            print(f"✗ {description:30} ({symbol:15}): {result['message'][:80]}")
            return False, result['message']
        else:
            print(f"? {description:30} ({symbol:15}): No close price")
            return False, "No close price"
    except Exception as e:
        print(f"✗ {description:30} ({symbol:15}): {str(e)[:80]}")
        return False, str(e)


print("="*80)
print("测试 Twelve Data API 符号可用性")
print("="*80)

# 测试美国国债的不同符号格式
print("\n【美国国债收益率】")
test_symbol("US10Y", "10年期国债 (US10Y)")
test_symbol("^TNX", "10年期国债 (^TNX)")
test_symbol("^IRX", "13周国债 (^IRX)")
test_symbol("^FVX", "5年期国债 (^FVX)")
test_symbol("^TYX", "30年期国债 (^TYX)")

print("\n等待 60 秒...")
time.sleep(60)

# 测试指数
print("\n【指数】")
test_symbol("VIX", "VIX恐慌指数 (VIX)")
test_symbol("^VIX", "VIX恐慌指数 (^VIX)")
test_symbol("SPX", "标普500指数 (SPX)")
test_symbol("^GSPC", "标普500指数 (^GSPC)")

print("\n等待 60 秒...")
time.sleep(60)

# 测试大宗商品
print("\n【大宗商品】")
test_symbol("XAU/USD", "黄金 (XAU/USD)")
test_symbol("XAG/USD", "白银 (XAG/USD)")
test_symbol("CL/USD", "原油 (CL/USD)")
test_symbol("WTI/USD", "原油 (WTI/USD)")
test_symbol("GC/USD", "黄金期货 (GC/USD)")
test_symbol("SI/USD", "白银期货 (SI/USD)")

print("\n等待 60 秒...")
time.sleep(60)

# 测试SOFR相关
print("\n【SOFR相关】")
test_symbol("SOFR/USD", "SOFR利率 (SOFR/USD)")
test_symbol("USD/SOFR", "SOFR利率 (USD/SOFR)")
test_symbol("SOFR", "SOFR (SOFR)")

print("\n等待 60 秒...")
time.sleep(60)

# 测试美联储数据
print("\n【美联储数据】")
test_symbol("RRPONTSYD", "隔夜逆回购")
test_symbol("IORB", "超额储备余额")
test_symbol("TGA", "TGA账户余额")

print("\n" + "="*80)
print("测试完成")
print("="*80)