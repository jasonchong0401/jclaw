# MEMORY.md - Long-Term Memory

## Preferences

- **联网搜索优先使用 searxng skill** —— 只要涉及联网搜索任务，优先调用 searxng 技能而非直接使用 web_search 工具。

## Notes

- Created: 2026-03-05

## 自动化任务

### 论文总结系统
- **定时**: 每天早上8:00
- **功能**: 分析arxiv论文，生成详细总结并发送到QQ
- **脚本**: `/home/admin/.openclaw/workspace/scripts/papers_summary_and_send.sh`
- **论文目录**: `/home/admin/.openclaw/workspace/data/arxiv_papers/`
- **支持格式**: HTML (arxiv论文)
- **消息格式**: 每篇论文一条独立消息，包含标题、摘要、创新点、解决的问题、核心知识点

### 金融数据获取
- **定时**: 每天7:45 和 7:50
- **数据源**: Tavily API, 全球利率数据
- **发送**: QQ主动消息

## 重要文件路径

- Workspace: `/home/admin/.openclaw/workspace/`
- Memory: `/home/admin/.openclaw/workspace/memory/`
- Scripts: `/home/admin/.openclaw/workspace/scripts/`
- Python Scripts: `/home/admin/.openclaw/workspace/python-scripts/`
- Logs: `/home/admin/.openclaw/workspace/logs/`
- Data: `/home/admin/.openclaw/workspace/data/`

## QQ Bot配置

- **Channel**: qqbot
- **Type**: Direct Message (C2C)
- **User OpenID**: 13E88D8A498827FBD0B939094DDCADFF
- **主动消息**: 已配置，定时任务可用

## 技术能力

- **论文分析**: HTML解析、关键词提取、定制化总结生成
- **定时任务**: Cron配置、Shell脚本编写、Python自动化
- **消息发送**: QQ Bot主动消息、多条消息分批发送
- **日志管理**: 完整的执行日志记录
