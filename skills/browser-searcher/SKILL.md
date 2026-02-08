---
name: browser-searcher
description: 使用Chrome浏览器自动化百度搜索，支持翻页查找M3U8视频资源，最多搜索100页，自动测试每个链接提取可用地址
license: 专有。LICENSE.txt 包含完整条款
version: 1.0.0
---

## 我做什么

[在此处详细描述技能的核心功能和使用场景]

## 何时使用我

[描述在什么情况下应该使用此技能]

## 使用流程

### 目录结构

```
browser-searcher/
├── SKILL.md              # 技能主配置文件
├── scripts/              # 脚本目录
│   ├── main.py          # 主执行脚本（位于 scripts/main.py）
│   └── requirements.txt # Python依赖文件（位于 scripts/requirements.txt）
└── LICENSE.txt          # 许可证文件
```

> 注意：以上目录结构中使用斜杠(/)是为了文档显示清晰，实际文件路径会根据操作系统自动使用正确的分隔符（Windows使用反斜杠\，Unix/Linux/macOS使用斜杠/）

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
├── scripts/          # 脚本目录
│   ├── main.py      # 主脚本
│   └── requirements.txt  # Python依赖
└── LICENSE.txt      # 许可证文件
```

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
- [ ] scripts目录已创建
- [ ] requirements.txt文件存在于scripts目录
- [ ] main.py示例脚本已创建（包含输出到当前工作目录的示例）
- [ ] 所有脚本存放在scripts目录下

**输出规则验证**:
- [ ] 脚本使用 `os.getcwd()` 获取当前工作目录作为输出路径
- [ ] 输出文件不保存到技能安装目录
