---
name: news-fetcher
description: 技能工具 - 专业的技能工具
license: 专有。LICENSE.txt 包含完整条款
version: 1.0.0
---

---
name: news-fetcher
description: "---
name: news-fetcher
description: 具有可自定义过滤选项的综合新闻抓取技能，从百度新闻获取新闻文章。此技能提供对当前新闻的结构化访问，包含完整文章的直接链接。
license: 完整条款见 LICENSE.txt
---

 新闻获取技能

 功能
- **实时新闻**：从百度新闻获取最新文章
- **类别过滤**：支持不同新闻类别（国内、国际、科技、娱乐）
- **可自定义数量**：每次请求检索 1-50 篇文章
- **丰富元数据**：返回标题、摘要、链接和时间戳
- **中文语言支持**：针对中文新闻内容优化

 使用方法
```javascript
const newsFetcher = require('news-fetcher');

// 获取前 10 条新闻（默认）
const result = await newsFetcher.getNews();

// 获取 5 条科技新闻文章
const techNews = await newsFetcher.getNews({
  count: 5,
  category: '科技'
});
```

 参数
- `count` (数字，可选)：要获取的文章数量（默认：10，最小：1，最大：50）
- `category` (字符串，可选)：新闻类别过滤器（默认：'综合'，选项：'国内'、'国际'、'科技'、'娱乐' 等）

 输出
返回包含以下内容的 JSON 对象：
- 新闻文章数组，每篇文章包含：
  - `title`：文章标题
  - `summary`：内容摘要
  - `link`：完整文章的直接 URL
  - `timestamp`：发布时间
  - `source`：新闻来源
- 返回文章总数
- 请求元数据

 依赖项
- axios ^1.6.0
- cheerio ^1.0.0-rc.12

 示例
```javascript
// 基本使用
const latestNews = await newsFetcher.getNews();

// 自定义类别和数量
const internationalNews = await newsFetcher.getNews({
  category: '国际',
  count: 15
});
```

 类别
数据处理、网络抓取、新闻聚合 - 专业的技能工具，用于..."
license: 专有。LICENSE.txt 包含完整条款
---

---
name: news-fetcher
description: 具有可自定义过滤选项的综合新闻抓取技能，从百度新闻获取新闻文章。此技能提供对当前新闻的结构化访问，包含完整文章的直接链接。
license: 完整条款见 LICENSE.txt
---

# 新闻获取技能

## 功能
- **实时新闻**：从百度新闻获取最新文章
- **类别过滤**：支持不同新闻类别（国内、国际、科技、娱乐）
- **可自定义数量**：每次请求检索 1-50 篇文章
- **丰富元数据**：返回标题、摘要、链接和时间戳
- **中文语言支持**：针对中文新闻内容优化

## 使用方法
```javascript
const newsFetcher = require('news-fetcher');

// 获取前 10 条新闻（默认）
const result = await newsFetcher.getNews();

// 获取 5 条科技新闻文章
const techNews = await newsFetcher.getNews({
  count: 5,
  category: '科技'
});
```

## 参数
- `count` (数字，可选)：要获取的文章数量（默认：10，最小：1，最大：50）
- `category` (字符串，可选)：新闻类别过滤器（默认：'综合'，选项：'国内'、'国际'、'科技'、'娱乐' 等）

## 输出
返回包含以下内容的 JSON 对象：
- 新闻文章数组，每篇文章包含：
  - `title`：文章标题
  - `summary`：内容摘要
  - `link`：完整文章的直接 URL
  - `timestamp`：发布时间
  - `source`：新闻来源
- 返回文章总数
- 请求元数据

## 依赖项
- axios ^1.6.0
- cheerio ^1.0.0-rc.12

## 示例
```javascript
// 基本使用
const latestNews = await newsFetcher.getNews();

// 自定义类别和数量
const internationalNews = await newsFetcher.getNews({
  category: '国际',
  count: 15
});
```

## 类别
数据处理、网络抓取、新闻聚合