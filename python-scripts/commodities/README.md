# 商品价格脚本

## 脚本列表

### 黄金和石油价格
- `get_gold_oil_prices.py` - 使用 Twelve Data API 获取黄金和石油价格
- `gold_oil_prices.py` - 使用 Scrapling 从 investing.com 获取实时价格
- `gold_oil_prices_alt.py` - 黄金石油价格获取（备用版本）

### SOFR 利率刮板
- `scraper.py` - 综合金融数据刮板（黄金、石油、SOFR、美债利率等）

## 使用方法

```bash
cd python-scripts/commodities
python 脚本名.py
```

## 数据源

- **Twelve Data API** - 需要的 API Key: 已配置在脚本中
- **Investing.com** - 通过 Scrapling 框架爬取
- **GoldAPI.io** - 黄金价格 API
- **FRED API** - SOFR 利率数据
- **EIA** - 石油价格数据