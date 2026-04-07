#!/usr/bin/env python3
"""
使用多种免费数据源获取金融数据
1. Yahoo Finance (yfinance)
2. Twelve Data API
3. FRED API (如果有有效 key)
"""

import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Twelve Data API 配置
TD_API_KEY = os.getenv('TWELVEDATA_API_KEY')
if not TD_API_KEY:
    raise ValueError("未找到 TWELVEDATA_API_KEY 环境变量，请在 .env 文件中配置")

# 数据配置
DATA_CONFIG = {
    'vix': {
        'name': 'VIX恐慌指数',
        'description': '芝加哥期权交易所波动率指数',
        'yahoo_symbol': '^VIX',
        'td_symbol': 'VIX',
        'fred_id': 'VIXCLS'
    },
    'gold': {
        'name': '黄金现货价格',
        'description': '伦敦黄金市场现货价格',
        'yahoo_symbol': 'GC=F',  # 黄金期货
        'td_symbol': 'XAU/USD',
        'fred_id': 'GOLDAMGBD228NLBM'
    },
    'silver': {
        'name': '白银现货价格',
        'description': '白银现货价格',
        'yahoo_symbol': 'SI=F',  # 白银期货
        'td_symbol': 'XAG/USD',
        'fred_id': 'SILVER'
    },
    'sofr': {
        'name': 'SOFR利率',
        'description': '担保隔夜融资利率',
        'yahoo_symbol': None,
        'td_symbol': 'SOFR',
        'fred_id': 'SOFR'
    },
    'us10y': {
        'name': '美国10年期国债收益率',
        'description': '10年期美国国债市场收益率',
        'yahoo_symbol': '^TNX',
        'td_symbol': 'US10Y',
        'fred_id': 'DGS10'
    },
    'tga': {
        'name': 'TGA账户余额',
        'description': '财政部一般账户余额 (美联储负债端)',
        'yahoo_symbol': None,
        'td_symbol': 'TGA',
        'fred_id': 'WTREGEN'
    },
    'excess_reserves': {
        'name': '超额储备余额',
        'description': '存款机构的超额准备金 (美联储负债端)',
        'yahoo_symbol': None,
        'td_symbol': 'IORB',
        'fred_id': 'EXCRESNS'
    },
    'reverse_repo': {
        'name': '隔夜逆回购余额',
        'description': '美联储隔夜逆回购操作余额 (美联储负债端)',
        'yahoo_symbol': None,
        'td_symbol': 'RRPONTSYD',
        'fred_id': 'RRPONTSYD'
    },
    'mbs': {
        'name': 'MBS持仓余额',
        'description': '美联储持有的抵押贷款支持证券 (美联储资产端)',
        'yahoo_symbol': None,
        'td_symbol': 'MBAL',
        'fred_id': 'MSLMSFRBAT'
    },
    'us2y': {
        'name': '美国2年期国债收益率',
        'description': '2年期美国国债市场收益率',
        'yahoo_symbol': '^FVX',
        'td_symbol': 'US2Y',
        'fred_id': 'DGS2'
    },
    'us5y': {
        'name': '美国5年期国债收益率',
        'description': '5年期美国国债市场收益率',
        'yahoo_symbol': '^FVX',
        'td_symbol': 'US5Y',
        'fred_id': 'DGS5'
    },
    'us30y': {
        'name': '美国30年期国债收益率',
        'description': '30年期美国国债市场收益率',
        'yahoo_symbol': '^TYX',
        'td_symbol': 'US30Y',
        'fred_id': 'DGS30'
    }
}


def get_yahoo_data(symbol):
    """从 Yahoo Finance 获取数据"""
    try:
        # 使用 Yahoo Finance API
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {
            'interval': '1d',
            'range': '1d',
            'includePrePost': 'false'
        }

        response = requests.get(url, params=params, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }, timeout=10)

        response.raise_for_status()
        data = response.json()

        if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
            result = data['chart']['result'][0]
            meta = result.get('meta', {})
            return {
                'price': meta.get('regularMarketPrice'),
                'currency': meta.get('currency'),
                'date': datetime.fromtimestamp(meta.get('regularMarketTime', 0)).strftime('%Y-%m-%d'),
                'exchange': meta.get('exchangeName')
            }
        return None
    except Exception as e:
        return {'error': str(e)}


def get_td_data(symbol):
    """从 Twelve Data API 获取数据"""
    try:
        url = "https://api.twelvedata.com/quote"
        params = {
            'symbol': symbol,
            'apikey': TD_API_KEY
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'close' in data:
            return {
                'price': float(data['close']),
                'date': data.get('datetime', datetime.now().strftime('%Y-%m-%d')),
                'exchange': data.get('exchange')
            }
        elif 'message' in data:
            return {'error': data['message']}
        return None
    except Exception as e:
        return {'error': str(e)}


def get_fed_data_from_fred(series_id):
    """从 FRED 获取美联储数据"""
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        'series_id': series_id,
        'api_key': 'demo',
        'file_type': 'json',
        'limit': 1,
        'sort_order': 'desc'
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'observations' in data and len(data['observations']) > 0:
                obs = data['observations'][0]
                if obs.get('value') and obs['value'] != '.':
                    return {
                        'value': float(obs['value']),
                        'date': obs['date']
                    }
        return None
    except Exception:
        return None


def main():
    """主函数"""
    results = {
        'timestamp': datetime.now().isoformat(),
        'data': {}
    }

    print("="*80)
    print("获取金融数据 (多数据源)")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # 按类别获取数据
    categories = {
        'market_data': ['vix', 'gold', 'silver', 'sofr', 'us10y', 'us2y', 'us5y', 'us30y'],
        'fed_liability': ['tga', 'excess_reserves', 'reverse_repo'],
        'fed_asset': ['mbs']
    }

    category_names = {
        'market_data': '市场数据',
        'fed_liability': '美联储负债端',
        'fed_asset': '美联储资产端'
    }

    for category, keys in categories.items():
        print(f"\n【{category_names[category]}】")
        results['data'][category] = {}

        for key in keys:
            if key in DATA_CONFIG:
                config = DATA_CONFIG[key]
                print(f"  获取 {config['name']}...")

                data = None
                source = None

                # 尝试 Yahoo Finance
                if config['yahoo_symbol']:
                    data = get_yahoo_data(config['yahoo_symbol'])
                    if data and 'error' not in data:
                        source = 'Yahoo Finance'

                # 如果 Yahoo 失败，尝试 Twelve Data
                if not data or 'error' in data:
                    data = get_td_data(config['td_symbol'])
                    if data and 'error' not in data:
                        source = 'Twelve Data'

                # 对于美联储数据，尝试 FRED
                if not data or 'error' in data:
                    if config['fred_id'] and any(x in key for x in ['tga', 'reserves', 'repo', 'mbs']):
                        data = get_fed_data_from_fred(config['fred_id'])
                        if data and 'error' not in data:
                            source = 'FRED'

                # 保存结果
                if data and 'error' not in data:
                    results['data'][category][key] = {
                        'name': config['name'],
                        'description': config['description'],
                        'value': data.get('price', data.get('value')),
                        'date': data.get('date'),
                        'source': source,
                        'success': True
                    }
                    value = data.get('price', data.get('value'))
                    print(f"    ✓ {config['name']}: {value} ({source}, {data.get('date', 'N/A')})")
                else:
                    error_msg = data.get('error', '获取失败') if isinstance(data, dict) else '获取失败'
                    results['data'][category][key] = {
                        'name': config['name'],
                        'description': config['description'],
                        'success': False,
                        'error': error_msg
                    }
                    print(f"    ✗ {config['name']}: {error_msg}")

    # 保存结果
    output_file = '/home/admin/.openclaw/workspace/data/financial_data_free.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 生成 QQ 消息
    message = f"""📊 金融数据报告 (多数据源)
━━━━━━━━━━━━━━━━━━
🕐 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""

    success_count = 0
    for category in ['market_data', 'fed_liability', 'fed_asset']:
        category_name = category_names[category]
        if category in results['data'] and results['data'][category]:
            message += f"【{category_name}】\n"

            for key, data in results['data'][category].items():
                if data['success']:
                    success_count += 1
                    value = data['value']
                    date = data['date']
                    source = data.get('source', '')

                    if '利率' in data['name'] or '收益率' in data['name'] or 'VIX' in data['name']:
                        message += f"✓ {data['name']}: {value:.4f}% ({date}) [{source}]\n"
                    elif '余额' in data['name'] or '持仓' in data['name']:
                        message += f"✓ {data['name']}: ${value:,.2f} ({date}) [{source}]\n"
                    else:
                        message += f"✓ {data['name']}: ${value:.2f} ({date}) [{source}]\n"

    if success_count == 0:
        message += "⚠️ 暂无可用数据\n"

    message += "\n💡 数据源: Yahoo Finance, Twelve Data, FRED"
    message += "\n━━━━━━━━━━━━━━━━━━"

    # 保存 QQ 消息
    notify_file = '/home/admin/.openclaw/workspace/data/qq_free_financial_notify.json'
    notify_data = {
        'timestamp': datetime.now().isoformat(),
        'message': message,
        'results': results
    }
    with open(notify_file, 'w', encoding='utf-8') as f:
        json.dump(notify_data, f, ensure_ascii=False, indent=2)

    print("\n" + "="*80)
    print("获取完成")
    print(f"成功: {success_count} 项")
    print(f"数据文件: {output_file}")
    print(f"QQ通知文件: {notify_file}")
    print("="*80)

    # 打印消息预览
    print("\n📱 QQ 通知消息预览:")
    print("-" * 80)
    print(message)
    print("-" * 80)

    return message


if __name__ == '__main__':
    message = main()
    print(f"\n✅ 消息已准备好")