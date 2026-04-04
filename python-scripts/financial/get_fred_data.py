#!/usr/bin/env python3
"""
使用 FRED (圣路易斯联邦储备银行) API 获取金融数据
FRED 提供免费 API，包含大量美国金融数据
"""

import requests
import json
from datetime import datetime

# FRED API 配置 (使用 demo key，生产环境需要注册获取自己的 key)
FRED_API_KEY = "demo"  # demo key 有调用限制

# 数据源映射
DATA_SOURCES = {
    'vix': {
        'series_id': 'VIXCLS',
        'name': 'VIX恐慌指数',
        'description': '芝加哥期权交易所波动率指数'
    },
    'gold': {
        'series_id': 'GOLDAMGBD228NLBM',
        'name': '黄金现货价格',
        'description': '伦敦黄金市场下午定盘价'
    },
    'silver': {
        'series_id': 'SILVER',
        'name': '白银现货价格',
        'description': '白银现货价格'
    },
    'sofr': {
        'series_id': 'SOFR',
        'name': 'SOFR利率',
        'description': '担保隔夜融资利率'
    },
    'us10y': {
        'series_id': 'DGS10',
        'name': '美国10年期国债收益率',
        'description': '10年期美国国债市场收益率'
    },
    'tga': {
        'series_id': 'WTREGEN',
        'name': 'TGA账户余额',
        'description': '财政部一般账户余额 (美联储负债端)'
    },
    'excess_reserves': {
        'series_id': 'EXCRESNS',
        'name': '超额储备余额',
        'description': '存款机构的超额准备金 (美联储负债端)'
    },
    'reverse_repo': {
        'series_id': 'RRPONTSYD',
        'name': '隔夜逆回购余额',
        'description': '美联储隔夜逆回购操作余额 (美联储负债端)'
    },
    'mbs': {
        'series_id': 'MSLMSFRBAT',
        'name': 'MBS持仓余额',
        'description': '美联储持有的抵押贷款支持证券 (美联储资产端)'
    },
    'us2y': {
        'series_id': 'DGS2',
        'name': '美国2年期国债收益率',
        'description': '2年期美国国债市场收益率'
    },
    'us5y': {
        'series_id': 'DGS5',
        'name': '美国5年期国债收益率',
        'description': '5年期美国国债市场收益率'
    },
    'us30y': {
        'series_id': 'DGS30',
        'name': '美国30年期国债收益率',
        'description': '30年期美国国债市场收益率'
    }
}


def get_fred_data(series_id):
    """从 FRED API 获取数据"""
    url = f"https://api.stlouisfed.org/fred/series/observations"
    params = {
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'limit': 1,  # 只获取最新一条
        'sort_order': 'desc'
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'observations' in data and len(data['observations']) > 0:
            obs = data['observations'][0]
            return {
                'value': obs.get('value'),
                'date': obs.get('date'),
                'realtime_start': obs.get('realtime_start'),
                'realtime_end': obs.get('realtime_end')
            }
        else:
            return None
    except Exception as e:
        return {'error': str(e)}


def main():
    """主函数"""
    results = {
        'timestamp': datetime.now().isoformat(),
        'data': {}
    }

    print("="*80)
    print("从 FRED 获取金融数据")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # 分类获取数据
    categories = {
        'market_data': ['vix', 'gold', 'silver', 'sofr', 'us10y'],
        'fed_liability': ['tga', 'excess_reserves', 'reverse_repo'],
        'fed_asset': ['mbs', 'us2y', 'us5y', 'us30y']
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
            if key in DATA_SOURCES:
                source = DATA_SOURCES[key]
                print(f"  获取 {source['name']}...")

                data = get_fred_data(source['series_id'])

                if data and 'error' not in data:
                    if data['value'] and data['value'] != '.':
                        results['data'][category][key] = {
                            'name': source['name'],
                            'description': source['description'],
                            'value': float(data['value']),
                            'date': data['date'],
                            'realtime_start': data['realtime_start'],
                            'success': True
                        }
                        print(f"    ✓ {source['name']}: {data['value']} ({data['date']})")
                    else:
                        results['data'][category][key] = {
                            'name': source['name'],
                            'description': source['description'],
                            'success': False,
                            'error': '无可用数据'
                        }
                        print(f"    ✗ {source['name']}: 无可用数据")
                else:
                    results['data'][category][key] = {
                        'name': source['name'],
                        'description': source['description'],
                        'success': False,
                        'error': data.get('error', '获取失败')
                    }
                    print(f"    ✗ {source['name']}: {data.get('error', '获取失败')}")

    # 保存结果
    output_file = '/home/admin/.openclaw/workspace/data/fred_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 生成 QQ 消息
    message = f"""📊 金融数据报告 (FRED)
━━━━━━━━━━━━━━━━━━
🕐 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

【市场数据】
"""

    success_count = 0
    for category in ['market_data', 'fed_liability', 'fed_asset']:
        category_name = category_names[category]
        if category in results['data'] and results['data'][category]:
            if category != 'market_data':
                message += f"\n【{category_name}】\n"

            for key, data in results['data'][category].items():
                if data['success']:
                    success_count += 1
                    value = data['value']
                    date = data['date']

                    if '利率' in data['name'] or '收益率' in data['name'] or 'VIX' in data['name']:
                        message += f"✓ {data['name']}: {value:.4f}% ({date})\n"
                    elif '余额' in data['name'] or '持仓' in data['name']:
                        message += f"✓ {data['name']}: ${value:,.2f} ({date})\n"
                    else:
                        message += f"✓ {data['name']}: ${value:.2f} ({date})\n"

    if success_count == 0:
        message += "⚠️ 暂无可用数据\n"

    message += f"\n📈 数据来源: FRED (圣路易斯联邦储备银行)"
    message += "\n💡 提示: 使用 demo API key，如需稳定访问请注册获取自己的 FRED API key"
    message += "\n━━━━━━━━━━━━━━━━━━"

    # 保存 QQ 消息
    notify_file = '/home/admin/.openclaw/workspace/data/qq_fred_notify.json'
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
    print(f"\n✅ 消息已准备好，可以发送到 QQ")