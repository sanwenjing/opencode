---
name: git-push-notify
version: 0.7.0
description: 执行git push并发送邮件和手机通知，支持网络不稳定时自动重试，失败时仅记录日志
depends:
- skill: email-sender
  min_version: 1.0.0
- skill: termux-api-controller
  min_version: 1.1.0
license: 专有。LICENSE.txt 包含完整条款
---

## 我做什么

[在此处详细描述技能的核心功能和使用场景]

## 何时使用我

[描述在什么情况下应该使用此技能]

## 使用流程

### 目录结构

```
git-push-notify/
├── SKILL.md              # 技能主配置文件
├── config/               # 配置文件目录（保存技能脚本使用的所有配置文件）
├── scripts/              # 脚本目录
│   ├── main.py          # 主执行脚本（位于 scripts/main.py）
│   └── requirements.txt # Python依赖文件（位于 scripts/requirements.txt）
└── LICENSE.txt          # 许可证文件
```

> 注意：以上目录结构中使用斜杠(/)是为了文档显示清晰，实际文件路径会根据操作系统自动使用正确的分隔符（Windows使用反斜杠\，Unix/Linux/macOS使用斜杠/）

### 配置文件目录（config/）

所有技能脚本使用的配置文件都应放在 `config/` 目录下，例如：
- API 配置文件（如 config/api_config.json）
- 模板文件（如 config/templates/）
- 数据文件（如 config/data/）

脚本中加载配置文件时应使用绝对路径或相对于当前工作目录的路径。

### 脚本索引

**编码声明**: 本技能所有脚本默认使用UTF-8编码，Windows系统下已配置UTF-8控制台输出。

| 脚本名称 | 脚本路径 | 功能描述 | 调用方式 |
|---------|---------|---------|---------|
| main.py | scripts/main.py | 主执行脚本 | `python scripts/main.py` |
| requirements.txt | scripts/requirements.txt | Python依赖列表 | `pip install -r scripts/requirements.txt` |

### 使用方法

[详细的使用说明，包括示例代码]

## 输出标准

### 目录结构标准
创建的技能必须具有以下目录结构：

```
技能名/
├── SKILL.md          # 技能主配置文件
├── config/           # 配置文件目录（保存技能脚本使用的所有配置文件）
├── scripts/          # 脚本目录
│   ├── main.py      # 主脚本
│   └── requirements.txt  # Python依赖
└── LICENSE.txt      # 许可证文件
```

### 配置文件目录规则（重要）
**config/ 目录用途**：专门用于存放技能脚本运行时所需的所有配置文件。

**配置文件类型**：
- API 配置文件（如 api_config.json, credentials.ini）
- 模板文件（如 templates/*.j2）
- 数据文件（如 data/*.json, data/*.csv）
- 环境变量文件（如 .env 示例文件）
- 其他运行时配置文件

**配置文件加载方式**：
```python
import os

# 方式一：相对于当前工作目录加载配置文件（推荐）
config_path = os.path.join(os.getcwd(), "config", "settings.json")

# 方式二：相对于技能目录加载（不推荐，可能导致路径问题）
# skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# config_path = os.path.join(skill_dir, "config", "settings.json")
```

**重要**：配置文件应放在 config/ 目录下，而不是硬编码在脚本中或放在 scripts/ 目录下。

### 输出文件规则（重要）
**规则**: 所有脚本生成的输出文件（如下载的文件、生成的报告、输出的数据等）必须保存到**当前工作目录**，而不是技能安装目录。

**原因**:
- 技能安装目录通常位于系统配置目录（如 `~/.config/opencode/skills/`）
- 用户希望在当前工作目录中看到输出结果
- 避免污染技能安装目录

**跨平台路径处理**:
在Python中处理路径时，始终使用 `os.path.join()` 来确保跨平台兼容性：
- Windows系统会自动使用反斜杠 `\` 作为路径分隔符
- Unix/Linux/macOS系统会自动使用斜杠 `/` 作为路径分隔符
- `os.path.join()` 会根据操作系统自动选择正确的分隔符

**实现方法**:
```python
import os

# 正确: 保存到当前工作目录（自动使用系统路径分隔符）
output_path = os.path.join(os.getcwd(), "output.txt")

# 正确: 构建多级路径（自动处理路径分隔符）
data_dir = os.path.join(os.getcwd(), "data", "output")
output_path = os.path.join(data_dir, "result.txt")

# 错误: 不要保存到脚本所在目录
# script_dir = os.path.dirname(os.path.abspath(__file__))
# output_path = os.path.join(script_dir, "output.txt")

# 错误: 不要硬编码路径分隔符
# output_path = "C:\Users\user\data\output.txt"  # 仅限Windows
# output_path = "/home/user/data/output.txt"  # 仅限Unix/Linux/macOS
```

### 依赖管理
- 所有Python依赖必须记录在 scripts/requirements.txt 文件中
- 使用标准的pip requirements格式
- 建议指定最低版本号，如: `package>=1.0.0`
- 常用依赖包括: pyyaml, requests, beautifulsoup4 等

## 类别
开发工具

## 验证清单

**基础验证**:
- [ ] 技能名称通过正则表达式验证 `^[a-z0-9]+(-[a-z0-9]+)*$`
- [ ] 名称长度在1-64字符范围内
- [ ] 描述长度在1-1024字符范围内

**文件验证**:
- [ ] YAML frontmatter格式正确
- [ ] 所有必需字段存在（name, description, license）
- [ ] SKILL.md文件编码为UTF-8

**目录结构验证**:
- [ ] config目录已创建（用于存放配置文件）
- [ ] scripts目录已创建
- [ ] requirements.txt文件存在于scripts目录
- [ ] main.py示例脚本已创建（包含输出到当前工作目录的示例）
- [ ] 所有脚本存放在scripts目录下

**输出规则验证**:
- [ ] 脚本使用 `os.getcwd()` 获取当前工作目录作为输出路径
- [ ] 输出文件不保存到技能安装目录
