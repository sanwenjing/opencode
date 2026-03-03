---
name: finance-news
description: 财经新闻获取工具，支持获取微博热搜、今日头条热搜等热点资讯，支持关键词筛选
version: 1.1.0
license: MIT License (见仓库根目录 LICENSE 文件)
---

## 我做什么

财经新闻获取工具，通过调用公开热搜API获取最新热点资讯：
- 微博热搜实时获取
- 今日头条热搜实时获取
- 关键词筛选功能
- 支持JSON和Markdown格式输出
- 支持输出到文件或stdout

## 何时使用我

- 需要获取最新热搜资讯时
- 需要监控特定关键词的热搜时
- 需要批量获取某个行业的热点时
- 需要将热点资讯保存到本地进行分析时

## 使用流程

### 目录结构

```
finance-news/
├── SKILL.md              # 技能主配置文件
├── config/               # 配置文件目录
│   └── config.json      # 技能配置文件
└── scripts/              # 脚本目录
    ├── main.py          # 主执行脚本
    └── requirements.txt # Python依赖文件
```

### 脚本索引

**编码声明**: 本技能所有脚本默认使用UTF-8编码，Windows系统下已配置UTF-8控制台输出。

| 脚本名称 | 脚本路径 | 功能描述 | 调用方式 |
|---------|---------|---------|---------|
| main.py | scripts/main.py | 主执行脚本，获取热搜资讯 | `python scripts/main.py [选项]` |
| requirements.txt | scripts/requirements.txt | Python依赖列表 | `pip install -r scripts/requirements.txt` |

### 使用方法

```bash
# 获取微博热搜
python scripts/main.py

# 获取热搜并筛选关键词
python scripts/main.py --keyword "A股"

# 指定来源
python scripts/main.py --source weibo

# 输出为Markdown格式
python scripts/main.py --format markdown

# 保存到文件
python scripts/main.py --output news.json
```

### 命令行参数

| 参数 | 说明 | 默认值 |
|-----|------|-------|
| --keyword, -k | 搜索关键词（筛选包含该关键词的热搜） | "" |
| --source, -s | 新闻源 (weibo/toutiao/baidu/all) | all |
| --format, -f | 输出格式 (json/markdown) | json |
| --output, -o | 输出文件路径（为空则输出到stdout） | "" |
| --max, -m | 最大新闻数量 | 20 |

## 输出标准

### 输出文件规则

所有脚本生成的输出文件必须保存到**当前工作目录**，而不是技能安装目录。

### 依赖管理

- requests>=2.28.0
- beautifulsoup4>=4.11.0
- lxml>=4.9.0

## 类别

数据获取、财经资讯、热搜
