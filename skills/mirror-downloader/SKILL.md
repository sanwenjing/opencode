---
name: mirror-downloader
description: "递归下载镜像站点文件的工具，支持自定义URL地址参数，可递归下载整个目录结构"
license: 专有。LICENSE.txt 包含完整条款
---

## 我做什么

递归下载镜像站点或网页目录的工具。可以：
- 递归下载指定URL下的所有文件和子目录
- **强制保持原目录层级结构**，自动保留完整的远程目录层级，包括主机名
- 支持多线程并发下载，大幅提升下载速度（默认50线程）
- 支持自定义下载延迟，避免请求过快
- 自动跳过已存在的文件，支持断点续传
- 支持多种镜像站点格式（HTML目录列表）
- **下载后自动校验文件完整性**，比对远程和本地文件数量

## 何时使用我

- 需要镜像整个网站或目录结构时
- 下载开源软件镜像站点的文件（如Alpine、Ubuntu等）
- 备份远程服务器上的文件目录
- 批量下载静态资源文件

## 使用流程

### 安装依赖

```bash
pip install -r scripts/requirements.txt
```

### 目录结构

```
recursive-mirror-downloader/
├── SKILL.md              # 技能主配置文件
└── scripts/              # 脚本目录
    ├── download.py      # 主下载脚本（位于 scripts/download.py）
    └── requirements.txt # Python依赖文件（位于 scripts/requirements.txt）
```

### 脚本索引

**编码声明**: 本技能所有脚本默认使用UTF-8编码，Windows系统下已配置UTF-8控制台输出。

| 脚本名称 | 脚本路径 | 功能描述 | 调用方式 |
|---------|---------|---------|---------|
| download.py | scripts/download.py | 递归下载主程序 | `python scripts/download.py [选项]` |
| requirements.txt | scripts/requirements.txt | Python依赖列表 | `pip install -r scripts/requirements.txt` |

### 使用方法

#### 基本用法

```bash
# 使用默认URL下载阿里云Alpine v3.23镜像
cd recursive-mirror-downloader
python scripts/download.py
```

#### 指定URL下载

```bash
# 下载指定URL的内容
python scripts/download.py -u https://mirrors.aliyun.com/alpine/v3.22/

# 下载其他镜像站点
python scripts/download.py -u https://mirrors.tuna.tsinghua.edu.cn/alpine/v3.23/
```

#### 指定输出目录

```bash
# 下载到指定目录
python scripts/download.py -u https://example.com/repo/ -o ./my-downloads
```

#### 设置下载参数

```bash
# 设置更长的延迟（避免请求过快被封）
python scripts/download.py -u https://example.com/ -d 2.0

# 设置超时时间
python scripts/download.py -u https://example.com/ -t 60

# 设置并发线程数（默认50，可根据网络调整）
python scripts/download.py -u https://example.com/ -w 100
```

#### 完整参数列表

```
选项:
  -h, --help            显示帮助信息
  -u URL, --url URL     要下载的基础URL (默认: https://mirrors.aliyun.com/alpine/v3.23/)
  -o OUTPUT, --output OUTPUT  输出目录路径 (默认: ./downloads)
  -d DELAY, --delay DELAY    每次请求之间的延迟（秒）(默认: 0.5)
  -t TIMEOUT, --timeout TIMEOUT  请求超时时间（秒）(默认: 30)
  -w WORKERS, --workers WORKERS  并发下载线程数 (默认: 50)
```

#### 目录结构说明

本工具**强制保留完整的远程目录层级结构**，包括主机名。

```bash
# 示例：下载 https://mirrors.aliyun.com/alpine/v3.23/main/x86_64/
python scripts/download.py -u https://mirrors.aliyun.com/alpine/v3.23/main/x86_64/

# 文件将保存到：downloads/mirrors.aliyun.com/alpine/v3.23/main/x86_64/...
```

```bash
# 示例：指定输出目录
python scripts/download.py -u https://example.com/path/ -o ./backup

# 文件将保存到：backup/example.com/path/...
```

## 输出标准

### 成功下载
- 文件保存到指定的输出目录
- **强制保持原目录层级结构**，保留远程服务器的完整目录层级，包括主机名
- 显示下载进度和统计信息

### 下载统计
- 成功下载的文件数
- 跳过的文件数（已存在）
- 失败的文件数及错误信息

### 文件完整性校验
下载完成后自动进行完整性校验：
- 比对远程文件总数和本地文件总数
- 显示成功、跳过、失败的文件数量
- 如有缺失文件，列出缺失的文件列表（最多显示前20个）
- 校验通过显示 ✓，未通过显示 ✗

## 类别
开发工具、网络工具、文件下载

## 验证清单

**基础验证**:
- [x] 技能名称通过正则表达式验证 `^[a-z0-9]+(-[a-z0-9]+)*$`
- [x] 名称长度在1-64字符范围内
- [x] 描述长度在1-1024字符范围内

**文件验证**:
- [x] YAML frontmatter格式正确
- [x] 所有必需字段存在（name, description, license）
- [x] SKILL.md文件编码为UTF-8

**目录结构验证**:
- [x] scripts目录已创建
- [x] requirements.txt文件存在于scripts目录
- [x] 所有脚本存放在scripts目录下
