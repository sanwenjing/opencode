---
name: skill-creator
description: "严格验证并创建符合OpenCode规范的新技能，同时提供完整的技能诊断和修复功能。当 Claude 需要创建新技能时用于：(1) 严格验证技能名称和描述格式，(2) 创建标准目录结构（包含scripts目录），(3) 生成符合规范的SKILL.md文件，(4) 验证YAML front matter格式。当需要修复技能时用于：(1) 诊断技能系统问题，(2) 修复YAML front matter缺失，(3) 清理技能缓存，(4) 验证技能完整性，(5) 修复名称不一致等问题"
license: 专有。LICENSE.txt 包含完整条款
---

## 我做什么

### 创建功能

#### 严格验证功能
- **技能名称验证**：严格按照正则表达式 `^[a-z0-9]+(-[a-z0-9]+)*$` 验证名称格式
- **名称长度检查**：确保名称长度在1-64个字符范围内
- **字符规范验证**：禁止以连字符开头或结尾，禁止连续连字符
- **描述长度验证**：确保描述在1-1024个字符范围内
- **目录名一致性检查**：验证目录名与技能名称完全匹配
- **YAML frontmatter验证**：确保所有必需字段存在且格式正确

#### 创建功能
- 创建标准目录结构：`技能名/SKILL.md` 和 `技能名/scripts/`
- 生成符合规范的SKILL.md模板文件
- 自动填充必需的YAML frontmatter字段
- 提供可选字段的标准模板
- 创建scripts目录用于存放所有脚本文件

#### 错误处理
- 提供详细的错误信息和修正建议
- 阻止不符合规范的技能创建
- 支持交互式错误修正指导

### 修复功能

#### 诊断功能
- **技能系统全面诊断**：扫描所有技能目录，检测潜在问题
- **YAML front matter检查**：验证格式正确性和必需字段完整性
- **名称一致性验证**：检查目录名与YAML中name字段是否匹配
- **编码问题检测**：识别文件编码错误
- **缓存状态检查**：检测Python缓存目录
- **依赖文件检查**：检查requirements.txt是否存在及格式正确性
- **系统配置验证**：检查技能目录存在性和权限

#### 修复功能
- **自动修复YAML front matter**：为缺失的技能添加标准front matter
- **修复缺失字段**：自动补全name、description、license等必需字段
- **修复名称不一致**：统一目录名与YAML中的技能名称
- **清理缓存**：安全移除__pycache__目录
- **交互式修复**：支持逐个确认修复操作
- **批量自动修复**：一键修复所有检测到的问题

#### 报告生成
- 生成详细的诊断报告
- 按严重程度分类问题（critical/high/medium/low）
- 记录已应用的修复操作
- 支持导出报告到文件

## 何时使用我

### 创建新技能时
当你需要创建新的OpenCode技能时使用此技能。此技能提供：
- **严格规范验证**：确保100%符合OpenCode官方规范
- **错误预防机制**：在创建前拦截所有可能的规范违规
- **详细错误报告**：提供具体的错误位置和修正方案
- **标准化输出**：生成完全符合官方标准的技能结构

### 修复现有技能时
当技能系统出现问题或需要维护时使用：
- **技能加载失败**：诊断并修复导致技能无法加载的问题
- **YAML格式错误**：修复front matter格式问题和字段缺失
- **名称不一致**：统一技能目录名和内部标识
- **系统维护**：定期诊断和清理缓存，保持系统健康
- **批量修复**：快速修复多个技能的常见问题

## 使用流程

### 创建流程

#### 严格验证阶段
1. **技能名称验证**
   - 检查长度（1-64字符）
   - 验证字符集（小写字母数字+连字符）
   - 检查连字符使用规范
   - 验证正则表达式匹配

2. **描述验证**
   - 检查长度（1-1024字符）
   - 确保内容具体性

3. **前置检查**
   - 验证目录名与名称一致性
   - 检查文件系统权限

#### 创建阶段
4. **目录结构创建**
   - 创建技能主目录
   - 创建scripts子目录

5. **SKILL.md文件生成**
   - 生成标准YAML frontmatter（包含 name, description, license 三个必需字段）
   - 自动添加标准 license 声明
   - 创建模板内容结构，必须包含目录结构和脚本位置说明

6. **Scripts目录设置**
   - 创建scripts目录
   - 创建requirements.txt文件（包含默认依赖 pyyaml>=6.0）
   - 设置目录权限
   - 验证目录结构完整性

#### 验证阶段
7. **最终验证**
   - 重新验证所有规范要求
   - 检查文件完整性
   - 验证YAML语法正确性
   - 验证scripts目录存在性
   - 验证SKILL.md包含完整的脚本索引和编码声明

8. **结果反馈**
   - 提供详细的创建报告
   - 列出所有验证通过项
   - 标记潜在的改进建议

### 修复流程

#### 诊断阶段
1. **执行诊断**
   ```bash
   python scripts/skill_fixer.py --diagnose-only --verbose
   ```
   - 扫描所有技能目录
   - 检测YAML front matter问题
   - 验证名称一致性
   - 检查缓存状态

2. **生成报告**
   ```bash
   python scripts/skill_fixer.py --output diagnosis_report.md
   ```
   - 查看问题详情
   - 按严重程度分类
   - 导出诊断报告

#### 修复阶段

**方式一：交互式修复（推荐）**
```bash
python scripts/skill_fixer.py --interactive --verbose
```
逐个确认每个修复操作，适合首次修复或重要技能。

**方式二：自动修复**
```bash
python scripts/skill_fixer.py --auto-fix
```
自动修复所有检测到的问题，适合批量处理。

**方式三：快速修复**
```bash
python scripts/quick_fix.py
```
仅修复缺失YAML front matter的常见问题，快速简单。

**方式四：安全修复**
```bash
python scripts/safe_fix.py
```
安全地添加front matter，避免重复修复，适合多次运行。

#### 验证修复
1. 重新运行诊断确认问题已解决
2. 检查修复后的技能是否能正常加载
3. 必要时重启应用程序

## 目录结构

```
skill-creator/
├── SKILL.md              # 本技能主配置文件
├── scripts/              # 脚本目录
│   ├── create_skill.py  # 主创建脚本：创建符合规范的新技能
│   ├── skill_fixer.py   # 主修复脚本：完整诊断和修复功能
│   ├── safe_fix.py      # 安全修复脚本：避免重复修复
│   └── quick_fix.py     # 快速修复脚本：简化常见问题修复
└── LICENSE.txt          # 许可证文件
```

## 脚本索引

**编码声明**: 本技能所有脚本默认使用UTF-8编码，Windows系统下已配置UTF-8控制台输出。

| 脚本名称 | 脚本路径 | 功能描述 | 调用方式 |
|---------|---------|---------|---------|
| create_skill.py | scripts/create_skill.py | 主创建工具：创建符合OpenCode规范的新技能，自动生成requirements.txt | `python scripts/create_skill.py <技能名> <描述> [选项]` |
| skill_fixer.py | scripts/skill_fixer.py | 主诊断修复工具：完整扫描、诊断、修复、报告生成 | `python scripts/skill_fixer.py [选项]` |
| safe_fix.py | scripts/safe_fix.py | 安全修复工具：智能检测避免重复修复 | `python scripts/safe_fix.py [技能目录]` |
| quick_fix.py | scripts/quick_fix.py | 快速修复工具：仅修复缺失YAML front matter | `python scripts/quick_fix.py [技能目录]` |

### 脚本详细说明

#### create_skill.py - 主技能创建工具
用于创建符合OpenCode规范的新技能，自动创建标准目录结构和文件。

**主要功能**：
- 严格验证技能名称格式（正则表达式 `^[a-z0-9]+(-[a-z0-9]+)*$`）
- 验证描述长度（1-1024字符）
- 创建标准目录结构：`技能名/SKILL.md` 和 `技能名/scripts/`
- 自动生成规范的SKILL.md文件（包含完整的YAML frontmatter）
- 自动创建scripts/requirements.txt文件管理Python依赖
- 支持更新现有技能的依赖
- 提供模拟运行模式（dry-run）预览创建结果

**使用方法**：
```bash
# 创建新技能
python scripts/create_skill.py my-new-skill "这是一个新技能的描述"

# 创建技能并指定依赖
python scripts/create_skill.py my-new-skill "技能描述" --deps pyyaml requests beautifulsoup4

# 模拟运行（不实际创建文件）
python scripts/create_skill.py my-new-skill "描述" --dry-run

# 更新现有技能的依赖
python scripts/create_skill.py --update-deps my-existing-skill --deps numpy pandas

# 指定技能目录路径
python scripts/create_skill.py my-skill "描述" --skills-dir /path/to/skills
```

**命令行选项**：
- `name`: 技能名称（必需，仅包含小写字母、数字和连字符）
- `description`: 技能描述（必需，1-1024字符）
- `--skills-dir`: 指定技能目录路径
- `--deps`: Python依赖包列表（空格分隔，如: pyyaml requests）
- `--dry-run`: 模拟运行，显示将要创建的结构但不实际创建
- `--update-deps`: 更新现有技能的requirements.txt

**创建输出**：
成功创建后将生成以下结构：
```
技能名/
├── SKILL.md              # 包含完整YAML frontmatter和模板内容
├── scripts/              # 脚本目录
│   └── requirements.txt  # Python依赖列表（自动生成）
```

**requirements.txt管理**：
- 创建时自动生成包含默认依赖（pyyaml）的requirements.txt
- 可通过 `--deps` 参数指定额外依赖
- 使用 `--update-deps` 可更新现有技能的依赖
- 支持依赖去重和排序

#### skill_fixer.py - 主诊断修复工具
完整的功能强大的技能诊断和修复工具。

**主要功能**：
- 全面诊断技能系统问题
- 检测YAML front matter缺失或错误
- 验证技能名称一致性
- 检查文件编码问题
- 清理Python缓存
- 生成诊断报告

**使用方法**：
```bash
# 仅诊断不修复
python scripts/skill_fixer.py --diagnose-only --verbose

# 交互式修复（逐个确认）
python scripts/skill_fixer.py --interactive

# 自动修复所有问题
python scripts/skill_fixer.py --auto-fix

# 指定技能目录
python scripts/skill_fixer.py --skills-dir /path/to/skills

# 导出诊断报告
python scripts/skill_fixer.py --output report.md

# 修复指定技能
python scripts/skill_fixer.py --skill skill-name --auto-fix
```

**命令行选项**：
- `--skills-dir`: 指定技能目录路径
- `--diagnose-only`: 仅执行诊断，不进行修复
- `--auto-fix`: 自动修复所有检测到的问题
- `--interactive`: 交互式修复，逐个确认
- `--skill`: 指定要修复的单个技能
- `--output`: 导出诊断报告到文件
- `--verbose`: 显示详细输出

#### safe_fix.py - 安全修复工具
安全地修复技能问题，避免重复添加YAML front matter。

**主要功能**：
- 智能检测已有front matter
- 清理重复的front matter块
- 安全添加缺失的front matter
- 避免对同一文件重复修复

**使用方法**：
```bash
# 修复当前目录下的所有技能
python scripts/safe_fix.py

# 修复指定目录下的技能
python scripts/safe_fix.py /path/to/skills
```

#### quick_fix.py - 快速修复工具
简化版的快速修复工具，专门处理最常见的问题。

**主要功能**：
- 快速扫描所有技能
- 仅修复缺失YAML front matter的问题
- 使用标准模板自动添加front matter
- 适合批量快速修复

**使用方法**：
```bash
# 快速修复当前目录下的所有技能
python scripts/quick_fix.py

# 快速修复指定目录下的技能
python scripts/quick_fix.py /path/to/skills
```

## 输出标准

### 目录结构标准
创建的技能必须具有以下目录结构：

```
技能名/
├── SKILL.md              # 技能主配置文件（必须包含目录结构和脚本位置说明）
├── scripts/              # 脚本目录（存放所有可执行脚本）
│   ├── main.py          # 主执行脚本
│   ├── requirements.txt # Python依赖列表（必需）
│   └── ...              # 其他脚本文件
└── LICENSE.txt          # 许可证文件（可选）
```

### 文件内容标准
- **必需frontmatter字段**：
  - `name`: 严格符合命名规范
  - `description`: 1-1024字符，具体明确
  - `license`: 许可证类型（必需，如：专有。LICENSE.txt 包含完整条款）
- **可选frontmatter字段**：
  - `compatibility`: 兼容性信息
  - `metadata`: 字符串到字符串的映射

### 依赖管理标准（重要）
所有新创建的技能必须包含依赖管理文件：

#### requirements.txt 要求
- **位置**: 必须位于 `scripts/requirements.txt`
- **格式**: 标准pip requirements格式
- **内容**: 列出所有Python依赖包及其最低版本
- **默认依赖**: 所有技能默认包含 `pyyaml>=6.0`

#### 依赖声明示例
```
# Python依赖列表
# 安装命令: pip install -r requirements.txt

pyyaml>=6.0
requests>=2.28.0
beautifulsoup4>=4.11.0
```

#### 依赖管理最佳实践
1. **始终使用版本号**: 建议指定最低版本，如 `package>=1.0.0`
2. **最小化依赖**: 只包含必需的依赖
3. **定期更新**: 及时更新依赖版本以修复安全漏洞
4. **测试兼容性**: 确保所有依赖版本兼容

### SKILL.md内容规范要求

创建新技能时，SKILL.md必须包含以下章节：

#### 1. 目录结构说明
必须在文档中明确说明技能的目录结构，包括：
- 技能主目录位置
- SKILL.md文件位置
- scripts目录位置及用途
- 各脚本文件的相对路径

**格式示例**：
```
### 目录结构
```
技能名/
├── SKILL.md              # 技能主配置文件
└── scripts/              # 脚本目录
    ├── main.py          # 主执行脚本（位于 scripts/main.py）
    └── helper.py        # 辅助脚本（位于 scripts/helper.py）
```
```

#### 2. 脚本索引章节
必须在文档中包含"脚本索引"章节，使用表格列出所有脚本信息：

| 脚本名称 | 脚本路径 | 功能描述 | 调用方式 |
|---------|---------|---------|---------|
| main.py | scripts/main.py | 主程序入口 | `python scripts/main.py` |
| helper.py | scripts/helper.py | 辅助函数库 | `import scripts.helper` |

**必须包含的信息**：
- **脚本名称**: 脚本的标识名称
- **脚本路径**: 相对于技能根目录的路径（如 `scripts/main.py`）
- **功能描述**: 脚本的主要功能（一句话描述）
- **调用方式**: 如何调用此脚本（命令或导入语句）

#### 3. 编码声明要求
- **强制要求**: 所有脚本文件必须使用UTF-8编码
- **声明位置**: 在"脚本索引"章节的开头必须声明：
  > **编码声明**: 本技能所有脚本默认使用UTF-8编码，Windows系统下已配置UTF-8控制台输出。
- **Python脚本特殊要求**: 所有Python脚本开头必须添加编码设置：
  ```python
  # 设置控制台编码为UTF-8
  import sys
  if sys.platform == 'win32':
      import io
      sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
      sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
  ```

#### 4. 脚本位置规范
- **位置要求**: 所有脚本必须存放在`scripts/`目录下，禁止放在技能根目录
- **命名规范**: 脚本文件名应简洁明了，使用小写字母、数字和下划线
- **禁止项**: 不得在根目录下存放任何可执行脚本文件

#### 5. 输出文件规则（重要）
**规则**: 所有脚本生成的输出文件（如下载的文件、生成的报告、输出的数据等）必须保存到**当前工作目录**，而不是技能安装目录。

**原因**:
- 技能安装目录通常位于系统配置目录（如 `~/.config/opencode/skills/`）
- 用户希望在当前工作目录中看到输出结果
- 避免污染技能安装目录

**跨平台路径处理（重要）**:
在Python中处理文件路径时，必须遵循以下规则以确保跨平台兼容性：

1. **使用 os.path.join()**: 始终使用 `os.path.join()` 来构建路径，它会根据操作系统自动选择正确的路径分隔符：
   - Windows: 自动使用反斜杠 `\\`
   - Unix/Linux/macOS: 自动使用斜杠 `/`

2. **禁止硬编码路径分隔符**:
   ```python
   # 错误示例 - 硬编码路径分隔符
   output_path = "C:\\Users\\user\\data\\output.txt"  # 仅限Windows
   output_path = "/home/user/data/output.txt"  # 仅限Unix/Linux/macOS
   
   # 错误示例 - 混用分隔符
   output_path = "data/output.txt"  # Windows上会失败
   ```

3. **正确使用 os.path.join()**:
   ```python
   import os
   
   # 正确 - 使用 os.path.join() 自动处理
   output_path = os.path.join(os.getcwd(), "output.txt")
   data_dir = os.path.join(os.getcwd(), "data")
   result_path = os.path.join(data_dir, "result.txt")
   
   # os.path.join() 会根据操作系统自动选择:
   # Windows: "C:\\Users\\user\\data\\result.txt"
   # Unix/Linux/macOS: "/home/user/data/result.txt"
   ```

4. **获取当前系统路径分隔符**（如需显示）:
   ```python
   path_sep = os.sep  # Windows: \\, Unix/Linux/macOS: /
   ```

**实现方法**:
```python
import os

# 正确: 保存到当前工作目录（自动使用系统路径分隔符）
output_path = os.path.join(os.getcwd(), "output.txt")

# 正确: 构建多级路径（自动处理路径分隔符）
data_dir = os.path.join(os.getcwd(), "data", "output")
result_path = os.path.join(data_dir, "result.txt")

# 错误: 不要保存到脚本所在目录
# script_dir = os.path.dirname(os.path.abspath(__file__))
# output_path = os.path.join(script_dir, "output.txt")

# 错误: 不要硬编码路径分隔符
# output_path = "C:\\Users\\user\\data\\output.txt"  # 仅限Windows
# output_path = "/home/user/data/output.txt"  # 仅限Unix/Linux/macOS
```

#### 5. 快速定位指南
为了帮助调用方快速定位脚本，SKILL.md应包含：
- 完整的文件树结构图
- 每个脚本的路径说明
- 调用示例中包含完整路径
- 如有多个脚本，说明脚本间的调用关系

### 完整的SKILL.md模板结构

创建新技能时，生成的SKILL.md应遵循以下完整结构：

```markdown
---
name: 技能名称
description: "技能描述"
license: 专有。LICENSE.txt 包含完整条款
---

## 我做什么
[功能描述，说明技能的核心功能]

## 何时使用我
[使用场景，说明在什么情况下使用此技能]

## 使用流程

### 目录结构
```
技能名/
├── SKILL.md              # 技能主配置文件
└── scripts/              # 脚本目录
    ├── main.py          # 主执行脚本（位于 scripts/main.py）
    └── helper.py        # 辅助脚本（位于 scripts/helper.py）
```

### 脚本索引
**编码声明**: 本技能所有脚本默认使用UTF-8编码，Windows系统下已配置UTF-8控制台输出。

| 脚本名称 | 脚本路径 | 功能描述 | 调用方式 |
|---------|---------|---------|---------|
| skill_fixer.py | scripts/skill_fixer.py | 主诊断修复工具：完整扫描、诊断、自动修复、报告生成 | `python scripts/skill_fixer.py [选项]` |
| safe_fix.py | scripts/safe_fix.py | 安全修复工具：避免重复修复，清理重复YAML front matter | `python scripts/safe_fix.py [技能目录]` |
| quick_fix.py | scripts/quick_fix.py | 快速修复工具：简化版YAML front matter修复 | `python scripts/quick_fix.py [技能目录]` |

### 使用方法
[详细的使用说明，包括示例代码]
## 输出标准

### 创建技能时的输出
- 标准目录结构：`技能名/SKILL.md` 和 `技能名/scripts/`
- 规范的SKILL.md文件，包含完整的YAML front matter和脚本索引
- 所有文件使用UTF-8编码

### 修复技能时的输出
- 诊断报告：显示发现的问题分类（critical/high/medium/low）
- 修复日志：列出已应用的修复操作
- 可选的Markdown格式诊断报告文件

## 类别
开发工具、技能创建、规范验证、技能修复、系统维护

### 验证清单
创建技能时必须检查以下所有项目：

**基础验证**：
- [ ] 技能名称通过正则表达式验证 `^[a-z0-9]+(-[a-z0-9]+)*$`
- [ ] 名称长度在1-64字符范围内
- [ ] 不包含非法字符或格式（不以连字符开头/结尾，无连续连字符）
- [ ] 描述长度在1-1024字符范围内
- [ ] 目录名与技能名称完全匹配

**文件验证**：
- [ ] YAML frontmatter格式正确
- [ ] 所有必需字段存在（name, description, license）
- [ ] license字段存在且格式正确
- [ ] SKILL.md文件编码为UTF-8

**目录结构验证**：
- [ ] scripts目录已创建
- [ ] requirements.txt文件已创建（位于scripts/目录）
- [ ] 所有脚本存放在scripts目录下
- [ ] 没有在根目录下存放脚本文件

**SKILL.md内容验证**：
- [ ] 包含"目录结构"章节，说明文件组织方式
- [ ] 包含"脚本索引"章节，使用表格列出所有脚本
- [ ] 脚本索引中包含脚本名称、路径、功能描述、调用方式
- [ ] 包含编码声明，明确说明使用UTF-8编码
- [ ] Python脚本包含UTF-8控制台编码设置代码
- [ ] 包含"输出文件规则"章节，说明输出到当前工作目录的要求

**输出规则验证**：
- [ ] 脚本使用 `os.getcwd()` 获取当前工作目录作为输出路径
- [ ] 输出文件不保存到技能安装目录

## 类别
开发工具、技能创建、规范验证、技能修复、系统维护
