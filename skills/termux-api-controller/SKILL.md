---
name: termux-api-controller
description: "在远程Termux设备上执行API命令的工具，依赖remote-manager技能"
version: "1.0.0"
depends:
  - skill: remote-manager
license: 专有。LICENSE.txt 包含完整条款
---

## 我做什么

在远程 Termux 设备上执行 API 命令的工具。通过 SSH 连接到 Termux 设备，调用 termux-api 包提供的各种 Android 功能接口。

## 何时使用我

当需要从电脑远程控制 Android 手机上的 Termux 时使用此技能，例如：
- 获取手机电池状态、位置信息
- 发送短信、拨打电话
- 控制手机振动、屏幕亮度、手电筒
- 读取剪贴板、发送通知
- 语音合成、指纹验证等

## 使用流程

### 前提条件

1. **手机安装 Termux**: 从 F-Droid 下载安装
2. **手机安装 Termux:API**: https://f-droid.org/packages/com.termux.api/
3. **手机安装 termux-api 包**: 在 Termux 中执行 `apt install termux-api`
4. **配置 SSH 连接**: 在 Termux 中安装 openssh 并配置
5. **配置 remote-manager**: 在 hosts.yaml 中添加 Termux 主机

### 目录结构

```
termux-api-controller/
├── SKILL.md              # 技能主配置文件
├── config/               # 配置文件目录
├── scripts/              # 脚本目录
│   └── main.py          # 主执行脚本
└── LICENSE.txt          # 许可证文件
```

### 脚本索引

**编码声明**: 本技能所有脚本默认使用UTF-8编码，Windows系统下已配置UTF-8控制台输出。

| 脚本名称 | 脚本路径 | 功能描述 | 调用方式 |
|---------|---------|---------|---------|
| main.py | scripts/main.py | Termux API 控制器 | `python scripts/main.py [命令] [参数]` |

### 使用方法

```bash
# 查看所有可用 API
python scripts/main.py list

# 执行 API 命令
python scripts/main.py battery-status
python scripts/main.py info
python scripts/main.py torch on
python scripts/main.py vibrate "-d 500"
python scripts/main.py clipboard-set "测试内容"
python scripts/main.py notification "-t 标题 -c 内容"

# 指定远程主机
python scripts/main.py battery-status --host termux
```

## 输出标准

### 输出文件规则（重要）
**规则**: 所有脚本生成的输出文件必须保存到**当前工作目录**，而不是技能安装目录。

```python
import os
output_path = os.path.join(os.getcwd(), "output.txt")
```

## 类别

移动设备控制、远程管理、Android API

## 验证清单

**基础验证**:
- [x] 技能名称通过正则表达式验证 `^[a-z0-9]+(-[a-z0-9]+)*$`
- [x] 名称长度在1-64字符范围内
- [x] 描述长度在1-1024字符范围内

**文件验证**:
- [x] YAML frontmatter格式正确
- [x] 所有必需字段存在（name, description, license, version）
- [x] SKILL.md文件编码为UTF-8

**目录结构验证**:
- [x] config目录已创建
- [x] scripts目录已创建
- [x] requirements.txt文件存在于scripts目录
- [x] main.py主脚本已创建

**依赖验证**:
- [x] 声明依赖 remote-manager 技能
