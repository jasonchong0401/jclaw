#!/usr/bin/env python3
"""
分析利率历史数据
查看多日利率变化趋势
"""

import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict

DB_PATH = '/home/admin/.openclaw/workspace/data/interest_rates.db'


def get_latest_rates():
    """获取最新的利率数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT r.country_code, r.country_name, c.flag, r.rate, r.timestamp
        FROM interest_rates r
        LEFT JOIN country_config c ON r.country_code = c.country_code
        WHERE r.id IN (
            SELECT MAX(id) FROM interest_rates GROUP BY country_code
        )
        ORDER BY r.rate DESC
    ''')

    results = []
    for row in cursor.fetchall():
        code, name, flag, rate, timestamp = row
        results.append({
            'code': code,
            'name': name,
            'flag': flag or '🏳️',
            'rate': rate,
            'timestamp': timestamp
        })

    conn.close()
    return results


def get_rates_by_date(date: str):
    """获取指定日期的利率数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT r.country_code, r.country_name, c.flag, r.rate, r.timestamp
        FROM interest_rates r
        LEFT JOIN country_config c ON r.country_code = c.country_code
        WHERE r.date = ?
        ORDER BY r.rate DESC
    ''', (date,))

    results = {}
    for row in cursor.fetchall():
        code, name, flag, rate, timestamp = row
        results[code] = {
            'name': name,
            'flag': flag or '🏳️',
            'rate': rate,
            'timestamp': timestamp
        }

    conn.close()
    return results


def get_rates_history(days: int = 7):
    """获取最近N天的利率历史"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    cursor.execute('''
        SELECT r.country_code, r.country_name, c.flag, r.rate, r.date, r.timestamp
        FROM interest_rates r
        LEFT JOIN country_config c ON r.country_code = c.country_code
        WHERE r.date >= ? AND r.date <= ?
        ORDER BY r.date DESC, r.country_code
    ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))

    # 按日期组织数据
    history = defaultdict(dict)
    for row in cursor.fetchall():
        code, name, flag, rate, date, timestamp = row
        history[date][code] = {
            'name': name,
            'flag': flag or '🏳️',
            'rate': rate,
            'timestamp': timestamp
        }

    conn.close()
    return dict(history)


def calculate_changes():
    """计算利率变化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 获取每个国家最近两次的记录
    cursor.execute('''
        SELECT r1.country_code, r1.country_name, c.flag, r1.rate as latest_rate,
               r1.timestamp as latest_timestamp, r2.rate as previous_rate
        FROM interest_rates r1
        LEFT JOIN country_config c ON r1.country_code = c.country_code
        LEFT JOIN interest_rates r2 ON r1.country_code = r2.country_code
            AND r2.id = (
                SELECT id FROM interest_rates r3
                WHERE r3.country_code = r1.country_code
                AND r3.id < r1.id
                ORDER BY id DESC LIMIT 1
            )
        WHERE r1.id IN (
            SELECT MAX(id) FROM interest_rates GROUP BY country_code
        )
        ORDER BY r1.country_code
    ''')

    changes = []
    for row in cursor.fetchall():
        code, name, flag, latest_rate, latest_timestamp, previous_rate = row
        if previous_rate is not None:
            change = latest_rate - previous_rate
            change_pct = ((latest_rate - previous_rate) / previous_rate) * 100 if previous_rate > 0 else 0
        else:
            change = 0
            change_pct = 0

        changes.append({
            'code': code,
            'name': name,
            'flag': flag or '🏳️',
            'latest_rate': latest_rate,
            'previous_rate': previous_rate,
            'change': change,
            'change_pct': change_pct,
            'timestamp': latest_timestamp
        })

    conn.close()
    return changes


def show_latest_rates():
    """显示最新利率"""
    print("\n" + "="*80)
    print("最新利率数据")
    print("="*80)

    rates = get_latest_rates()

    for i, data in enumerate(rates, 1):
        print(f"{i}. {data['flag']} {data['name']}: {data['rate']}%")
        print(f"   更新时间: {data['timestamp']}")

    return rates


def show_rates_history(days: int = 7):
    """显示利率历史"""
    print("\n" + "="*80)
    print(f"最近 {days} 天利率历史")
    print("="*80)

    history = get_rates_history(days)

    if not history:
        print("暂无历史数据")
        return

    # 按日期排序
    sorted_dates = sorted(history.keys(), reverse=True)

    for date in sorted_dates:
        print(f"\n📅 {date}")
        print("-" * 40)

        # 按利率排序
        rates = sorted(history[date].items(), key=lambda x: x[1]['rate'], reverse=True)

        for code, data in rates:
            print(f"  {data['flag']} {data['name']}: {data['rate']}%")


def show_rate_changes():
    """显示利率变化"""
    print("\n" + "="*80)
    print("利率变化分析")
    print("="*80)

    changes = calculate_changes()

    if not changes:
        print("暂无数据用于对比")
        return

    print("\n国家        | 最新利率 | 上次利率 | 变化    | 变化%")
    print("-" * 60)

    for change in changes:
        prev = f"{change['previous_rate']}%" if change['previous_rate'] is not None else "N/A"
        delta = f"{change['change']:+.2f}%" if change['change'] != 0 else "-"
        delta_pct = f"{change['change_pct']:+.2f}%" if change['change_pct'] != 0 else "-"

        print(f"{change['flag']} {change['name']:8s} | {change['latest_rate']:.2f}%   | {prev:>7s} | {delta:>6s} | {delta_pct:>6s}")


def show_statistics():
    """显示统计信息"""
    print("\n" + "="*80)
    print("数据库统计")
    print("="*80)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 总记录数
    cursor.execute('SELECT COUNT(*) FROM interest_rates')
    total_records = cursor.fetchone()[0]

    # 国家数量
    cursor.execute('SELECT COUNT(DISTINCT country_code) FROM interest_rates')
    total_countries = cursor.fetchone()[0]

    # 日期范围
    cursor.execute('SELECT MIN(date), MAX(date) FROM interest_rates')
    date_range = cursor.fetchone()

    # 每个国家的记录数
    cursor.execute('''
        SELECT r.country_code, r.country_name, c.flag, COUNT(*) as count
        FROM interest_rates r
        LEFT JOIN country_config c ON r.country_code = c.country_code
        GROUP BY r.country_code
        ORDER BY count DESC
    ''')

    country_counts = []
    for row in cursor.fetchall():
        code, name, flag, count = row
        country_counts.append((code, name, flag or '🏳️', count))

    conn.close()

    print(f"总记录数: {total_records}")
    print(f"国家数量: {total_countries}")
    print(f"数据日期范围: {date_range[0]} ~ {date_range[1]}")

    print("\n各国记录数:")
    print("-" * 40)
    for code, name, flag, count in country_counts:
        print(f"  {flag} {name}: {count} 条")


def main():
    """主函数"""
    import sys

    print("="*80)
    print("利率数据分析工具")
    print("="*80)
    print(f"数据库: {DB_PATH}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 根据参数执行不同功能
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'latest':
            show_latest_rates()
        elif command == 'history':
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            show_rates_history(days)
        elif command == 'changes':
            show_rate_changes()
        elif command == 'stats':
            show_statistics()
        else:
            print(f"未知命令: {command}")
            print("可用命令: latest, history [days], changes, stats")
    else:
        # 默认显示所有信息
        show_latest_rates()
        show_rate_changes()
        show_rates_history(3)
        show_statistics()


if __name__ == '__main__':
    main()