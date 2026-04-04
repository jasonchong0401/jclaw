# Python Scripts

这个文件夹包含所有的 Python 脚本，按功能分类组织。

## 目录结构

### 📁 `financial/` - 金融数据脚本
- 利率分析、经济数据获取、金融数据处理等

### 📁 `commodities/` - 商品价格脚本
- 黄金、石油价格获取
- SOFR 利率刮板

### 📁 `llm/` - LLM 论文相关
- LLM 论文摘要和发送

### 📁 根目录 - 其他脚本
- `email_processor.py` - 邮件处理
- `test_symbols.py` - 测试股票代码

## 快速导航

**金融数据：**
```bash
cd python-scripts/financial
python get_fred_data.py
```

**商品价格：**
```bash
cd python-scripts/commodities
python get_gold_oil_prices.py
```

**LLM 论文：**
```bash
cd python-scripts/llm
python llm_paper_digest.py
```

## 依赖安装

```bash
pip install twelvedata requests beautifulsoup4 scrapling
```