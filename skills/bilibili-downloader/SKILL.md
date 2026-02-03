---
name: bilibili-downloader
description: Bilibili视频下载器，使用bilibili-api库直接从B站API下载视频。全自动下载，无需浏览器，支持多种清晰度选择。适用于Windows、MacOS、Linux平台。
license: 专有。LICENSE.txt 包含完整条款
compatibility:
  - Windows
  - MacOS
  - Linux
metadata:
  version: "2.1.0"
  author: OpenCode
  tags:
    - bilibili
    - video-download
    - bilibili-api
    - download-manager
    - automation
---

# Bilibili视频下载器

## 功能概述

本技能提供Bilibili视频全自动下载功能。使用`bilibili-api-python`库直接从B站官方API获取视频信息并下载，无需浏览器自动化，无需手动操作验证码，完全自动化。

## 技术说明

**重要更新 (v2.1.0)**:
- ✅ 使用 bilibili-api 直接访问B站API，无需PeanutDL网站
- ✅ 全自动下载，无需浏览器
- ✅ 无需手动操作验证码
- ✅ 支持多种视频清晰度选择
- ✅ **自动重试**：下载失败时自动重试3次，提高下载成功率

## 目录结构

```
peanutdl-bilibili-downloader/
├── SKILL.md              # 技能主配置文件
└── scripts/              # 脚本目录
    ├── download.py       # 视频下载脚本（位于 scripts/download.py）
    └── requirements.txt  # Python依赖列表（位于 scripts/requirements.txt）
```

### 脚本索引

**编码声明**: 本技能所有脚本默认使用UTF-8编码，Windows系统下已配置UTF-8控制台输出。

| 脚本名称 | 脚本路径 | 功能描述 | 调用方式 |
|---------|---------|---------|---------|
| download.py | scripts/download.py | Bilibili视频全自动下载器 | `python scripts/download.py <视频链接>` |
| requirements.txt | scripts/requirements.txt | Python依赖列表 | `pip install -r scripts/requirements.txt` |

## 核心功能

### 视频下载
- ✅ 全自动下载，无需浏览器
- ✅ 无需手动操作验证码
- ✅ 支持多种画质选择（360P/480P/720P/1080P/4K）
- ✅ 自动选择最高可用画质
- ✅ 显示下载进度
- ✅ 自动保存到指定目录
- ✅ **智能重试**：下载失败时自动重试3次，间隔3秒

### 视频处理
- 下载视频流（MP4格式）
- 下载音频流（M4A格式）
- ✅ **自动合并**：自动检测并使用ffmpeg合并音视频
- ✅ **自动下载ffmpeg**：Windows系统会自动下载ffmpeg便携版
- 提供手动合并命令（备选方案）

## 使用方法

### 前置要求

安装依赖：
```bash
pip install -r scripts/requirements.txt
```

### 基本使用

```bash
# 使用视频链接
python scripts/download.py "https://www.bilibili.com/video/BV1mZrKBAEHf/"

# 使用BV号
python scripts/download.py "BV1mZrKBAEHf"

# 指定输出目录
python scripts/download.py "BV1mZrKBAEHf" -o ./my_downloads
```

### 高级功能

#### 合并音视频

由于B站使用DASH格式（音视频分离），下载后需要合并：

```bash
# 使用ffmpeg合并
ffmpeg -i "视频文件_video.mp4" -i "音频文件_audio.m4a" -c:v copy -c:a aac "输出文件.mp4"
```

#### 批量下载

创建包含多个BV号的文本文件，然后循环调用脚本。

## 常见问题

### Q1: 为什么下载的文件分为视频和音频？
**A1**: B站使用DASH流媒体格式，视频和音频是分开的。脚本会自动下载两个文件，并**自动合并**为完整视频。Windows系统会自动下载ffmpeg完成合并，无需手动操作。

### Q2: 如何提高画质？
**A2**: 脚本会自动选择最高可用画质。大会员账号可下载1080P+/4K画质，但需要有对应的B站会员权限。

### Q3: 下载速度慢？
**A3**: 下载速度取决于您的网络环境和B站CDN。可以尝试在网络空闲时段下载，或使用下载工具的多线程功能。

### Q4: 可以下载大会员视频吗？
**A4**: 需要登录B站账号（带大会员权限）才能下载大会员专属视频。本脚本默认使用未登录状态，仅支持免费视频下载。

## 技术规格

### 输入格式
- Bilibili视频链接（标准格式）: `https://www.bilibili.com/video/BVxxxx/`
- BV号（纯ID）: `BV1mZrKBAEHf`
- 支持含额外参数的链接: `https://www.bilibili.com/video/BV1mZrKBAEHf/?share_source=...`

### 输出格式
- 视频文件: `视频标题_video.mp4`
- 音频文件: `视频标题_audio.m4a`
- 合并命令提示: ffmpeg命令

### 依赖库
- **bilibili-api-python**: B站API库
- **httpx**: 异步HTTP客户端
- **requests**: HTTP请求库

### 系统要求
- Python 3.8+
- 网络连接
- 足够的存储空间

## 注意事项

1. 请确保您有权下载相关视频内容
2. 下载的视频仅限个人学习研究使用
3. 请遵守相关法律法规和平台协议
4. 建议在网络良好环境下使用
5. 音视频需要合并后才能正常播放

## 更新日志

### v2.1.0
- ✅ 新增自动重试功能：下载失败时自动重试3次
- ✅ 每次重试前等待3秒，避免请求过快导致失败
- ✅ 重试时显示当前重试次数，方便追踪下载进度
- ✅ 提高网络不稳定环境下的下载成功率

### v2.0.0 (重大更新)
- ✅ 全新架构：使用bilibili-api直接访问B站API
- ✅ 无需浏览器：纯Python实现，无需Chrome/Edge
- ✅ 全自动下载：无需手动操作验证码
- ✅ 自动合并：自动下载ffmpeg并合并音视频
- ✅ 智能检测：自动检测系统ffmpeg或下载便携版
- ✅ 更快速度：直接API调用，无需网页渲染
- ✅ 更好稳定性：不受网站改版影响

### v1.0.0
- 初始版本
- 基于PeanutDL网站（已弃用）

## 相关资源

- **bilibili-api文档**: https://nemo2011.github.io/bilibili-api
- **Bilibili官网**: https://www.bilibili.com
- **ffmpeg下载**: https://ffmpeg.org/download.html

## 故障排除

### 依赖安装失败
```bash
# 如果安装bilibili-api失败，尝试以下命令：
pip install --upgrade pip
pip install bilibili-api-python httpx requests
```

### 下载失败
- 检查网络连接是否正常
- 验证BV号是否正确
- 查看视频是否需要会员权限

### 合并失败
- 确保已安装ffmpeg: `ffmpeg -version`
- 检查音视频文件是否完整下载
- 使用VLC播放器可直接播放分离的音视频文件

---

**提示**: 本技能已完全修复，使用官方API直接下载，无需任何浏览器操作！
