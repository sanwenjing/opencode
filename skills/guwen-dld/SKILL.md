---
name: guwen-dld
description: "下载并拼接TXT古籍书籍的工具，支持从古文岛等网站抓取多章节内容并合并为完整文件"
version: "1.0.0"
license: MIT License (见仓库根目录 LICENSE 文件)
---

# Skill: guwen-dld

## 概述

这是一个用于下载和拼接TXT书籍或文档的工具，可以从网页抓取多章节内容并合并为完整的TXT文件。

## 功能特性

- 从网页URL批量获取内容
- 自动识别章节结构
- 拼接多个章节为一个完整TXT文件
- 支持古文书籍、在线文档等多种网页内容

## 目录结构

```
txt-downloader/
├── SKILL.md              # 本技能主配置文件
├── CHANGELOG.md          # 版本变更日志
├── config/               # 配置文件目录
└── scripts/              # 脚本目录
    └── main.py          # 主程序脚本
```

## 脚本索引

| 脚本名称 | 脚本路径 | 功能描述 | 调用方式 |
|---------|---------|---------|---------|
| main.py | scripts/main.py | 下载并拼接TXT文件 | python scripts/main.py --url "<网址>" --output "<输出文件>" |

## 使用方法

### 基本用法

```bash
python scripts/main.py --url "https://example.com/book" --output "book.txt"
```

### 参数说明

- `--url` 或 `-u`: 要下载的网页URL
- `--output` 或 `-o`: 输出文件路径（默认保存到当前工作目录）
- `--encoding`: 输出文件编码（默认UTF-8）

### 示例

```bash
# 下载单页内容
python scripts/main.py --url "https://www.gushiwen.cn/guwen/book.aspx?id=210" --output "渊海子平.txt"

# 指定编码
python scripts/main.py --url "https://example.com/book" --output "book.txt" --encoding "gbk"
```

## 配置文件

配置文件位于 `config/config.json`，可配置默认输出目录、编码等选项。

## 输出规则

- 输出文件保存到当前工作目录
- 不保存到技能安装目录
