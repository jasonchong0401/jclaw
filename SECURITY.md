# 安全配置说明

## TwelveData API Key 安全

为了防止 API Key 泄露到 GitHub，已采取以下措施：

### 1. 创建 `.env` 文件
在 workspace 根目录创建了 `.env` 文件，包含：
```env
TWELVEDATA_API_KEY=7420db1f72684a8893044c4f4ae54fc5
FRED_API_KEY=your_fred_api_key_here
```

### 2. 更新 `.gitignore`
添加了以下规则以防止敏感文件被提交：
```gitignore
# Environment variables (may contain sensitive info)
.env
.env.local
.env.*.local
```

### 3. 更新所有 Python 脚本
以下文件已更新为从环境变量读取 API Key：
- `python-scripts/financial/financial_data.py`
- `python-scripts/financial/financial_data_qq.py`
- `python-scripts/financial/get_free_financial_data.py`
- `python-scripts/commodities/get_gold_oil_prices.py`
- `python-scripts/test_symbols.py`

所有脚本现在都使用以下方式读取配置：
```python
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取 API Key
API_KEY = os.getenv('TWELVEDATA_API_KEY')
if not API_KEY:
    raise ValueError("未找到 TWELVEDATA_API_KEY 环境变量，请在 .env 文件中配置")
```

### 4. 安装依赖
已安装 `python-dotenv` 包来支持 `.env` 文件的读取：
```bash
pip3 install --user python-dotenv
```

## 使用方法

### 本地运行
所有脚本将自动从 `.env` 文件读取配置，无需任何修改。

### 生产环境
在生产环境或服务器上，可以通过以下方式设置环境变量：

**方法 1: 导出环境变量**
```bash
export TWELVEDATA_API_KEY="your_api_key_here"
python3 script.py
```

**方法 2: 在命令行中设置**
```bash
TWELVEDATA_API_KEY="your_api_key_here" python3 script.py
```

**方法 3: 使用服务器环境变量配置**
在 Docker、systemd 或其他部署配置中设置环境变量。

## 安全建议

1. **永远不要提交 `.env` 文件到 GitHub**
   - `.gitignore` 已配置，但请手动确认

2. **定期轮换 API Key**
   - 如果怀疑密钥泄露，立即在 TwelveData 后台重新生成

3. **使用不同的 Key**
   - 开发、测试、生产环境使用不同的 API Key

4. **监控 API 使用情况**
   - 在 TwelveData 后台监控异常调用

5. **示例文件**
   - 可以创建 `.env.example` 文件（不包含真实密钥）并提交到 GitHub
   - 新用户可以复制并填入自己的密钥

## 故障排除

如果脚本提示 "未找到 TWELVEDATA_API_KEY 环境变量"：

1. 检查 `.env` 文件是否存在于 workspace 根目录
2. 确认 `.env` 文件中的格式正确（没有多余的空格或引号）
3. 确认已安装 `python-dotenv` 包
4. 检查文件权限是否可读

```bash
ls -la /home/admin/.openclaw/workspace/.env
cat /home/admin/.openclaw/workspace/.env
```

## 验证配置

运行以下命令验证配置是否正确：

```bash
cd /home/admin/.openclaw/workspace/python-scripts
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key:', os.getenv('TWELVEDATA_API_KEY', 'NOT FOUND'))"
```

应该输出你的 API Key（而不是 NOT FOUND）。