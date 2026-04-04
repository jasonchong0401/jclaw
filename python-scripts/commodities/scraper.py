import requests
from bs4 import BeautifulSoup

# 定义爬虫类
class FinancialDataScraper:
    def __init__(self):
        self.session = requests.Session()

    def get_gold_price(self):
        try:
            url = 'https://www.goldapi.io/api/XAU/USD'  # 示例金价API
            headers = {'x-access-token': 'your_api_key'}  # 替换为实际API密钥
            response = self.session.get(url, headers=headers)
            return response.json().get('price', 'N/A')
        except Exception:
            return 'N/A'

    def get_oil_price(self):
        try:
            url = 'https://www.eia.gov/opendata/qb.php?sdid=PET.WCESTUS1.W'  # 示例石油期货价格API
            response = self.session.get(url)
            return 'Available' if response.status_code == 200 else 'N/A'
        except Exception:
            return 'N/A'

    def get_sofr_rate(self):
        try:
            url = 'https://api.stlouisfed.org/fred/series/observations?series_id=SOFR&api_key=your_api_key&file_type=json'  # 示例SOFR利率API
            response = self.session.get(url)
            data = response.json()
            return data['observations'][-1]['value'] if data else 'N/A'
        except Exception:
            return 'N/A'

    def get_us_10y_bond_rate(self):
        try:
            url = 'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2023/all?field_tdr_date_value=2023&type=daily_treasury_yield_curve'  # 示例十年期美债利率数据
            response = self.session.get(url)
            return 'Available' if response.status_code == 200 else 'N/A'
        except Exception:
            return 'N/A'

    def get_fed_mbs_holdings(self):
        try:
            url = 'https://www.federalreserve.gov/releases/h41/current/default.htm'  # 示例Fed MBS持仓网页
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            return 'Available' if soup else 'N/A'
        except Exception:
            return 'N/A'

    def get_fed_liabilities(self):
        try:
            url = 'https://www.federalreserve.gov/releases/h41/current/default.htm'  # 示例Fed负债端数据网页
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            return 'Available' if soup else 'N/A'
        except Exception:
            return 'N/A'

def send_qq_message(message):
    # 使用 qqbot 发送消息
    qqbot_command = f"qq send buddy your_qq_number '{message}'"  # 替换为您的QQ号
    import os
    os.system(qqbot_command)

if __name__ == '__main__':
    scraper = FinancialDataScraper()
    results = [
        f'Gold Price: {scraper.get_gold_price()}',
        f'Oil Price: {scraper.get_oil_price()}',
        f'SOFR Rate: {scraper.get_sofr_rate()}',
        f'10Y Bond Rate: {scraper.get_us_10y_bond_rate()}',
        f'Fed MBS Holdings: {scraper.get_fed_mbs_holdings()}',
        f'Fed Liabilities: {scraper.get_fed_liabilities()}'
    ]
    result_text = '\n'.join(results)
    print(result_text)
    send_qq_message(result_text)
