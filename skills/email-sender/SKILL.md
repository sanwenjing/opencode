---
name: email-sender
description: "专业的邮件发送工具，支持自动生成主题、配置文件管理账号信息、文件附件发送、文件夹打包发送、命令行调用"
version: "1.1.0"
license: 专有。LICENSE.txt 包含完整条款
---

## 我做什么

专业的邮件发送工具，提供以下核心功能：

1. **配置文件管理** - 通过JSON配置文件管理SMTP服务器、端口、账号、密码等信息
2. **自动生成主题** - 根据配置自动生成带时间戳的邮件主题
3. **文件附件发送** - 支持发送单个或多个文件附件
4. **文件夹打包发送** - 支持将文件夹自动打包成ZIP后发送
5. **命令行调用** - 完整的命令行参数支持，方便集成到脚本和工作流

## 何时使用我

- 需要自动化发送邮件的场景
- 需要通过脚本批量发送邮件
- 需要将文件或文件夹作为邮件附件发送
- 需要集成到CI/CD流程中自动发送报告

## 使用流程

### 配置文件说明

首次使用前，需要创建配置文件 `email_sender_config.json`：

```json
{
    "smtp_server": "smtp.example.com",
    "smtp_port": 465,
    "use_ssl": true,
    "username": "your_email@example.com",
    "password": "your_password",
    "from_name": "Email Sender",
    "default_to": "",
    "auto_subject_prefix": "[自动邮件]",
    "subject_date_format": "%Y-%m-%d %H:%M"
}
```

### 目录结构

```
email-sender/
├── SKILL.md              # 技能主配置文件
├── scripts/              # 脚本目录
│   ├── main.py          # 主执行脚本
│   └── requirements.txt # Python依赖文件
└── LICENSE.txt          # 许可证文件
```

### 脚本索引

**编码声明**: 本技能所有脚本默认使用UTF-8编码，Windows系统下已配置UTF-8控制台输出。

| 脚本名称 | 脚本路径 | 功能描述 | 调用方式 |
|---------|---------|---------|---------|
| main.py | scripts/main.py | 主执行脚本，邮件发送核心功能 | `python scripts/main.py [参数]` |
| requirements.txt | scripts/requirements.txt | Python依赖列表 | `pip install -r scripts/requirements.txt` |

### 使用方法

#### 1. 初始化配置文件

```bash
python scripts/main.py --init-config
```

这将在当前目录创建 `email_sender_config.json` 配置文件，然后编辑该文件填入您的邮件账号信息。

#### 2. 发送简单邮件

```bash
python scripts/main.py --to "receiver@example.com" --body "这是一封测试邮件"
```

#### 3. 发送带主题的邮件

```bash
python scripts/main.py -t "receiver@example.com" -s "邮件主题" -b "邮件正文"
```

#### 4. 发送带附件的邮件

```bash
# 单个文件
python scripts/main.py -t "receiver@example.com" -a /path/to/file.txt

# 多个文件
python scripts/main.py -t "receiver@example.com" -a file1.txt -a file2.pdf
```

#### 5. 发送文件夹（自动打包）

```bash
# 文件夹会自动打包成ZIP发送
python scripts/main.py -t "receiver@example.com" -a /path/to/folder
```

#### 6. 从文件读取邮件正文

```bash
python scripts/main.py -t "receiver@example.com" -s "报告" -f /path/to/body.txt
```

#### 7. 完整示例

```bash
python scripts/main.py \
    --to "receiver@example.com" \
    --subject "每日报告" \
    --body "请查收今日工作报告" \
    --attachment /path/to/report.pdf \
    --attachment /path/to/data_folder
```

### 命令行参数

| 参数 | 简写 | 说明 |
|-----|-----|------|
| --to | -t | 收件人邮箱（必需） |
| --subject | -s | 邮件主题（留空则自动生成） |
| --body | -b | 邮件正文 |
| --body-file | -f | 邮件正文文件路径 |
| --attachment | -a | 附件文件或文件夹（可多次使用） |
| --config | -c | 配置文件路径 |
| --init-config | -i | 创建默认配置文件 |
| --yes | -y | 跳过确认直接发送邮件 |

## 输出标准

### 配置文件说明

配置文件 `email_sender_config.json` 包含以下字段：

| 字段 | 说明 | 示例 |
|-----|------|------|
| smtp_server | SMTP服务器地址 | smtp.gmail.com |
| smtp_port | SMTP端口 | 465 (SSL) 或 587 (TLS) |
| use_ssl | 是否使用SSL | true/false |
| username | 邮箱账号 | your_email@gmail.com |
| password | 邮箱密码或应用专用密码 | xxxx |
| from_name | 发件人显示名称 | Email Sender |
| default_to | 默认收件人（可选） | |
| auto_subject_prefix | 自动生成主题的前缀 | [自动邮件] |
| subject_date_format | 自动生成主题的时间格式 | %Y-%m-%d %H:%M |

### 常见邮件服务商配置

**Gmail:**
- smtp_server: smtp.gmail.com
- smtp_port: 465
- use_ssl: true
- 注意：需要开启"应用专用密码"

**QQ邮箱:**
- smtp_server: smtp.qq.com
- smtp_port: 465
- use_ssl: true
- 注意：需要开启SMTP服务并获取授权码

**企业邮箱:**
- 根据企业邮箱配置相应SMTP服务器和端口

## 类别

开发工具、邮件处理

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
- [x] main.py主脚本已创建
- [x] 所有脚本存放在scripts目录下

**功能验证**:
- [x] 支持配置文件管理账号信息
- [x] 支持自动生成邮件主题
- [x] 支持文件附件发送
- [x] 支持文件夹打包发送
- [x] 支持命令行调用

**输出规则验证**:
- [x] 脚本使用 `os.getcwd()` 获取当前工作目录作为输出路径
- [x] 输出文件不保存到技能安装目录
- [x] 配置文件保存到当前工作目录
