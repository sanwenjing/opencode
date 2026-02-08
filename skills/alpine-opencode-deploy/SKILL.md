---
name: alpine-opencode-deploy
description: 在远程Alpine Linux服务器上自动部署和安装OpenCode AI编程助手，经过2026-02-08验证的最简部署流程
license: 专有。LICENSE.txt 包含完整条款
version: 1.0.0
---

## 我做什么

本技能用于在远程Alpine Linux服务器上自动部署和安装OpenCode AI编程助手。

### 核心功能

1. **SSH连接管理** - 通过SSH连接到远程Alpine服务器
2. **环境准备** - 安装bash和curl
3. **Node.js安装** - 下载完整Node.js包（含npm）
4. **OpenCode安装** - npm全局安装
5. **路径优化** - 找到正确的musl版本，创建符号链接

## 成功部署经验

### 🚀 最简部署流程（2026-02-08验证成功）

```bash
# 1. SSH连接并安装工具
apk add --no-cache bash curl

# 2. 下载完整Node.js包（包含npm）
curl -L -o node.tar.xz https://nodejs.org/dist/v20.10.0/node-v20.10.0-linux-x64.tar.xz

# 3. 解压安装到系统
tar -xf node.tar.xz
cp -r node-v20.10.0-linux-x64/bin/* /usr/local/bin/
cp -r node-v20.10.0-linux-x64/lib/* /usr/local/lib/

# 4. npm全局安装OpenCode
npm install -g opencode-ai

# 5. 找到正确的musl版本
find /usr/lib/node_modules/opencode-ai -name opencode -type f
# 通常是: opencode-linux-x64-musl/bin/opencode

# 6. 创建符号链接
ln -sf /usr/lib/node_modules/opencode-ai/node_modules/opencode-linux-x64-musl/bin/opencode /usr/local/bin/opencode

# 7. 验证
opencode --version
```

### 关键经验总结

| 步骤 | 经验 | 说明 |
|------|------|------|
| 1 | 不要用Alpine的nodejs包 | 不包含npm |
| 2 | 用完整Node.js包 | x64版本包含npm 10.2.3 |
| 3 | npm安装opencode-ai | 自动下载正确的musl版本 |
| 4 | 找到正确的二进制 | opencode-linux-x64-musl |
| 5 | 创建符号链接 | 方便全局访问 |

### 验证记录

| 日期 | 服务器 | 系统 | OpenCode版本 | 状态 |
|------|--------|------|--------------|------|
| 2026-02-08 | 192.168.31.150:2222 | Alpine 3.23 | 1.1.53 | ✅ 成功 |
| 2026-02-08 | 192.168.31.150:2223 | Alpine 3.23 | 1.1.53 | ✅ 成功 |

## 何时使用我

当您需要：
- 在新的Alpine Linux服务器上快速安装OpenCode
- 自动化OpenCode的部署流程
- 批量部署OpenCode到多台服务器
- 远程配置OpenCode开发环境

## 使用流程

### 目录结构

```
alpine-opencode-deploy/
├── SKILL.md              # 技能主配置文件
└── scripts/              # 脚本目录
    ├── main.py          # 主执行脚本（位于 scripts/main.py）
    └── requirements.txt # Python依赖文件（位于 scripts/requirements.txt）
```

> 注意：以上目录结构中使用斜杠(/)是为了文档显示清晰，实际文件路径会根据操作系统自动使用正确的分隔符（Windows使用反斜杠\，Unix/Linux/macOS使用斜杠/）

### 脚本索引

**编码声明**: 本技能所有脚本默认使用UTF-8编码，Windows系统下已配置UTF-8控制台输出。

| 脚本名称 | 脚本路径 | 功能描述 | 调用方式 |
|---------|---------|---------|---------|
| main.py | scripts/main.py | 在远程Alpine服务器上部署OpenCode | `python scripts/main.py` |
| requirements.txt | scripts/requirements.txt | Python依赖列表 | `pip install -r scripts/requirements.txt` |

### 使用方法

#### 1. 安装依赖

```bash
# 进入技能目录
cd C:\Users\Administrator\.config\opencode\skills\alpine-opencode-deploy

# 安装Python依赖
pip install -r scripts\requirements.txt
```

#### 2. 运行部署脚本

```bash
python scripts/main.py
```

脚本会提示您输入：

- **服务器地址**: 目标Alpine服务器的IP地址或域名（默认: 192.168.31.150）
- **SSH端口**: SSH服务端口（默认: 2222）
- **用户名**: SSH登录用户名（默认: root）
- **密码**: SSH登录密码（默认: admin）
- **安装选项**: 是否安装bash、是否使用官方脚本、是否创建符号链接

#### 3. 使用OpenCode

部署成功后，登录服务器：

```bash
ssh root@192.168.31.150 -p 2222
# 密码: admin

# 使用OpenCode
opencode --version
opencode --help
```

### 输出文件

部署过程中会在**当前工作目录**生成以下文件：

| 文件名 | 说明 |
|--------|------|
| opencode_deployment.log | 完整的部署日志 |

### 部署日志示例

```
============================================================
OpenCode部署日志
============================================================
目标服务器: 192.168.31.150:2222

[1/6] 连接 192.168.31.150:2222...
SSH连接成功!

[2/6] 安装 bash 和 curl...

[3/6] 下载完整Node.js包...

[4/6] 解压安装Node.js和npm...
v20.10.0
10.2.3

[5/6] 安装 OpenCode...
added 5 packages in 12s

[6/6] 查找正确的OpenCode...
找到: /usr/lib/node_modules/opencode-ai/node_modules/opencode-linux-x64-musl/bin/opencode
版本: 1.1.53

============================================================
使用说明
============================================================
SSH登录: ssh root@192.168.31.150 -p 2222
密码: admin
使用命令: opencode
============================================================

*** OpenCode部署成功! ***
```

### 程序化调用

也可以在Python代码中直接调用部署函数：

```python
import sys
sys.path.insert(0, 'scripts')
from main import deploy_opencode

# 执行部署
result = deploy_opencode(
    hostname='192.168.31.150',
    port=2222,
    username='root',
    password='admin'
)

# 检查结果
if result['success']:
    print(f"OpenCode版本: {result['opencode_version']}")
    print(f"安装路径: {result['opencode_path']}")
else:
    print(f"部署失敗: {result['error']}")

# 返回值说明
# result = {
#     "success": True/False,           # 是否成功
#     "hostname": "192.168.31.150",    # 服务器地址
#     "port": 2222,                   # SSH端口
#     "node_version": "v24.13.0",     # Node.js版本
#     "opencode_path": "...",         # OpenCode安装路径
#     "opencode_version": "1.1.53",    # OpenCode版本
#     "error": None,                   # 错误信息
#     "log_file": "..."               # 日志文件路径
# }
```

## 输出文件规则（重要）

**规则**: 所有脚本生成的输出文件（如日志文件、配置文件等）必须保存到**当前工作目录**，而不是技能安装目录。

**原因**:
- 技能安装目录通常位于系统配置目录（如 `~/.config/opencode/skills/`）
- 用户希望在当前工作目录中看到输出结果
- 避免污染技能安装目录

**跨平台路径处理**:
在Python中处理路径时，始终使用 `os.path.join()` 来确保跨平台兼容性：

```python
import os

# 正确: 保存到当前工作目录（自动使用系统路径分隔符）
output_path = os.path.join(os.getcwd(), "output.txt")

# 正确: 构建多级路径（自动处理路径分隔符）
data_dir = os.path.join(os.getcwd(), "data", "output")
result_path = os.path.join(data_dir, "result.txt")
```

### 依赖管理

- **paramiko>=3.0.0** - SSH/SFTP客户端库
- **pyyaml>=6.0** - YAML配置文件处理

所有依赖必须记录在 `scripts/requirements.txt` 文件中，使用标准pip requirements格式。

## 类别

DevOps、服务器管理、自动化部署、Alpine Linux、OpenCode

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
- [x] main.py脚本已创建（包含输出到当前工作目录的示例）
- [x] 所有脚本存放在scripts目录下

**输出规则验证**:
- [x] 脚本使用 `os.getcwd()` 获取当前工作目录作为输出路径
- [x] 输出文件不保存到技能安装目录
