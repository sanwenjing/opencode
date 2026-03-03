---
name: stock-quote
description: 专业的实时股票行情获取工具，支持获取A股、港股市场的实时行情数据
version: 1.2.1
license: MIT License (见仓库根目录 LICENSE 文件)
---

## 我做什么

专业的实时股票行情获取工具，支持：
- **A股市场**：上海证券交易所、深圳证券交易所（6位数字代码）
- **港股市场**：香港证券交易所（5位数字代码）
- **美股市场**：纽约证券交易所、纳斯达克（字母代码，如AAPL）
- 自动识别股票市场类型
- 批量查询多只股票
- 输出JSON格式数据

## 何时使用我

当您需要快速查询股票实时行情时使用此技能：
- 获取股票当前价格、涨跌幅
- 查看开盘价、最高价、最低价
- 查询成交量、成交额
- 批量获取多只股票数据

## 使用方法

### 脚本索引

**编码声明**: 本技能所有脚本默认使用UTF-8编码，Windows系统下已配置UTF-8控制台输出。

| 脚本名称 | 脚本路径 | 功能描述 | 调用方式 |
|---------|---------|---------|---------|
| main.py | scripts/main.py | 主执行脚本：获取实时股票行情 | `python "C:\Users\Administrator\.config\opencode\skills\stock-quote\scripts\main.py"` |

### 命令行参数

```
股票代码 [股票代码 ...] [-m {a,hk,us,auto}] [-o 输出文件] [-v]
```

**参数说明**：
- `symbols`: 股票代码（支持多个）
- `-m, --market`: 指定市场类型 (a/hk/us/auto，默认auto自动识别)
- `-o, --output`: 输出JSON文件路径
- `-v, --verbose`: 显示详细信息

### 使用示例

```bash
# 查询A股上证指数
python "C:\Users\Administrator\.config\opencode\skills\stock-quote\scripts\main.py" 600519

# 查询A股平安银行
python "C:\Users\Administrator\.config\opencode\skills\stock-quote\scripts\main.py" 000001

# 查询港股腾讯控股
python "C:\Users\Administrator\.config\opencode\skills\stock-quote\scripts\main.py" 00700

# 查询美股苹果
python "C:\Users\Administrator\.config\opencode\skills\stock-quote\scripts\main.py" AAPL

# 批量查询多只股票
python "C:\Users\Administrator\.config\opencode\skills\stock-quote\scripts\main.py" 600519 000001 600036

# 指定查询A股市场
python "C:\Users\Administrator\.config\opencode\skills\stock-quote\scripts\main.py" 600519 -m a

# 保存到JSON文件
python "C:\Users\Administrator\.config\opencode\skills\stock-quote\scripts\main.py" 600519 -o stock.json
```

## 目录结构

```
stock-realtime-quote/
├── SKILL.md              # 技能主配置文件
├── config/               # 配置文件目录
│   └── config.example.json
└── scripts/              # 脚本目录
    ├── main.py          # 主执行脚本
    └── requirements.txt # Python依赖
```

## 输出文件规则

脚本运行后会在当前工作目录生成输出文件（如指定 -o 参数）。

## 依赖说明

无需额外安装依赖，仅使用Python标准库：
- urllib
- ssl
- re
- json
- argparse
- datetime
