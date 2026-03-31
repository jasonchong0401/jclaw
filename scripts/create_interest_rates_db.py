#!/usr/bin/env python3
"""
创建利率数据库
"""

import sqlite3
from datetime import datetime

DB_PATH = '/home/admin/.openclaw/workspace/data/interest_rates.db'

def create_database():
    """创建利率数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 创建利率数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interest_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_code TEXT NOT NULL,
            country_name TEXT NOT NULL,
            rate REAL NOT NULL,
            unit TEXT NOT NULL,
            source TEXT,
            timestamp TEXT NOT NULL,
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_country_date ON interest_rates(country_code, date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON interest_rates(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON interest_rates(date)')

    # 创建配置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS country_config (
            country_code TEXT PRIMARY KEY,
            country_name TEXT NOT NULL,
            flag TEXT,
            query TEXT NOT NULL,
            pattern TEXT NOT NULL,
            unit TEXT NOT NULL
        )
    ''')

    # 插入国家配置
    countries = {
        'CN': {'name': '中国', 'flag': '🇨🇳', 'query': 'current money market interest rate China 2026', 'pattern': r'([0-9.]+)%', 'unit': '%'},
        'US': {'name': '美国', 'flag': '🇺🇸', 'query': 'current federal funds rate USA United States 2026', 'pattern': r'([0-9.]+)%', 'unit': '%'},
        'EU': {'name': '欧洲', 'flag': '🇪🇺', 'query': 'current European Central Bank ECB deposit facility rate 2026', 'pattern': r'([0-9.]+)%', 'unit': '%'},
        'JP': {'name': '日本', 'flag': '🇯🇵', 'query': 'current Bank of Japan BOJ short-term interest rate policy rate 2026', 'pattern': r'([0-9.]+)%', 'unit': '%'},
        'CA': {'name': '加拿大', 'flag': '🇨🇦', 'query': 'current Bank of Canada overnight rate target 2026', 'pattern': r'([0-9.]+)%', 'unit': '%'},
        'AU': {'name': '澳洲', 'flag': '🇦🇺', 'query': 'current Reserve Bank of Australia RBA cash rate target 2026', 'pattern': r'([0-9.]+)%', 'unit': '%'}
    }

    for code, config in countries.items():
        cursor.execute('''
            INSERT OR REPLACE INTO country_config (country_code, country_name, flag, query, pattern, unit)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (code, config['name'], config['flag'], config['query'], config['pattern'], config['unit']))

    conn.commit()
    conn.close()

    print(f"✅ 数据库创建成功: {DB_PATH}")
    print(f"   国家配置: {len(countries)} 个")

if __name__ == '__main__':
    create_database()