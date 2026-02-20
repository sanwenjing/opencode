---
name: skill-creator
description: 严格验证并创建符合OpenCode规范的新技能，同时提供完整的技能诊断和修复功能。当 Claude 需要创建新技能时用于：(1) 严格验证技能名称和描述格式，(2)
  创建标准目录结构（包含scripts目录），(3) 生成符合规范的SKILL.md文件，(4) 验证YAML front matter格式，(5) 版本管理和变更日志记录。当需要修复技能时用于：(1)
  诊断技能系统问题，(2) 修复YAML front matter缺失，(3) 清理技能缓存，(4) 验证技能完整性，(5) 修复名称不一致等问题，(6) 更新技能版本和变更日志
license: MIT License (见仓库根目录 LICENSE 文件)
version: 1.3.0
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
- 创建标准目录结构：`技能名/SKILL.md`、`技能名/config/` 和 `技能名/scripts/`
- 生成符合规范的SKILL.md模板文件
- 自动填充必需的YAML frontmatter字段
- 提供可选字段的标准模板
- 创建config目录用于存放技能脚本使用的所有配置文件
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
- **版本管理**：自动为新技能设置初始版本号

### 版本管理时
当需要管理技能版本时使用：
- **版本更新**：每次修改技能后自动更新版本号
- **变更记录**：自动记录版本变更日志到CHANGELOG.md
- **版本查询**：查看技能的当前版本和变更历史
- **版本规范**：遵循语义化版本规范（Semantic Versioning）

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

### 版本管理流程

#### 版本规范
所有技能必须遵循语义化版本规范（Semantic Versioning）：
- **版本格式**：`MAJOR.MINOR.PATCH`（如：1.0.0）
- **MAJOR**：主版本号 - 重大功能变更或不兼容的API修改
- **MINOR**：次版本号 - 新增功能（向下兼容）
- **PATCH**：修订号 - bug修复（向下兼容）

#### 版本管理命令

**更新版本并记录日志**
```bash
# 更新版本并添加变更日志
python scripts/version_manager.py --skill skill-name --version 1.1.0 --message "新增批量执行功能"

# 自动递增版本号（PATCH）
python scripts/version_manager.py --skill skill-name --bump patch --message "修复连接超时bug"

# 自动递增版本号（MINOR）
python scripts/version_manager.py --skill skill-name --bump minor --message "新增导出CSV功能"

# 自动递增版本号（MAJOR）
python scripts/version_manager.py --skill skill-name --bump major --message "重构API，不兼容旧版本"
```

**查看版本信息**
```bash
# 查看技能当前版本
python scripts/version_manager.py --skill skill-name --info

# 查看变更日志
python scripts/version_manager.py --skill skill-name --changelog
```

#### CHANGELOG.md 格式

每个技能必须包含 `CHANGELOG.md` 文件，记录所有版本变更：

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-15

### Added
- 初始版本发布
- 主机管理功能
- 批量命令执行功能

## [1.1.0] - 2024-01-20

### Added
- 新增操作系统版本自动获取功能
- 新增refresh命令

### Changed
- 优化连接超时处理
- 改进错误提示信息

### Fixed
- 修复exec命令参数冲突问题

## [1.1.1] - 2024-01-22

### Fixed
- 修复删除主机时的bug
```

## 技能修改规则

### 自动更新要求

修改任何现有技能时，必须自动更新以下文件：

1. **SKILL.md** - 更新 `version` 字段
2. **CHANGELOG.md** - 添加新版本记录

### 版本号规范

遵循语义化版本规范（Semantic Versioning v2.0.0）：

| 版本类型 | 规则 | 示例 |
|---------|------|------|
| **MAJOR** | 重大功能变更或不兼容的API修改 | 1.0.0 → 2.0.0 |
| **MINOR** | 新增功能（向下兼容） | 1.0.0 → 1.1.0 |
| **PATCH** | Bug修复或小优化 | 1.0.0 → 1.0.1 |

### 版本号判断标准

- **重大功能变更或重构** → MINOR + 1（重置PATCH为0）
- **新功能添加** → MINOR + 1
- **Bug修复或优化** → PATCH + 1

### CHANGELOG记录要求

每次版本更新必须在 `CHANGELOG.md` 中记录：

```markdown
## [1.1.0] - 2026-02-08

### Added
- 新增xxx功能

### Changed
- 优化xxx实现

### Fixed
- 修复xxx问题

### Verified
- 验证环境：xxx
```

### 技能修改自动流程

修改技能时，Claude 必须执行以下步骤：

1. **判断变更类型**：根据修改内容确定版本号递增类型
2. **读取当前版本**：从 SKILL.md 中获取当前版本号
3. **计算新版本**：按规范递增版本号
4. **更新 SKILL.md**：修改 version 字段
5. **更新 CHANGELOG.md**：添加新版本记录，包括：
   - 版本号
   - 修改日期
   - 变更内容分类（Added/Changed/Fixed/Verified）
   - 具体描述
6. **验证完整性**：确认两个文件都已正确更新

### 版本号判断示例

| 修改内容 | 版本类型 | 原因 |
|---------|---------|------|
| 添加新功能函数 | MINOR | 新增功能 |
| 优化现有代码 | PATCH | 优化改进 |
| 修复bug | PATCH | Bug修复 |
| 重构API | MINOR | 重大变更 |
| 更新文档 | PATCH | 文档优化 |
| 添加验证清单 | MINOR | 功能增强 |

#### YAML Front Matter 版本字段

**必需字段**：
- `version`: 当前版本号（必需，如：1.0.0）

**示例**：
```yaml
---
name: my-skill
description: "技能描述"
version: "1.0.0"
license: MIT License (见仓库根目录 LICENSE 文件)
---
```

## 目录结构

```
skill-creator/
├── SKILL.md              # 本技能主配置文件
├── CHANGELOG.md          # 版本变更日志
├── config/               # 配置文件目录（保存技能脚本使用的所有配置文件）
├── scripts/              # 脚本目录
│   ├── create_skill.py  # 主创建脚本：创建符合规范的新技能
│   ├── skill_fixer.py   # 主修复脚本：完整诊断和修复功能
│   ├── version_manager.py  # 版本管理脚本：更新版本号和变更日志
│   ├── safe_fix.py      # 安全修复脚本：避免重复修复
│   └── quick_fix.py     # 快速修复脚本：简化常见问题修复
└── LICENSE.txt          # 许可证文件
```

### 配置文件目录（config/）

所有技能脚本使用的配置文件都应放在 `config/` 目录下，例如：
- API 配置文件（如 config/api_config.json）
- 模板文件（如 config/templates/）
- 数据文件（如 config/data/）

脚本中加载配置文件时应使用绝对路径或相对于当前工作目录的路径。

## 脚本索引

**编码声明**: 本技能所有脚本默认使用UTF-8编码，Windows系统下已配置UTF-8控制台输出。

| 脚本名称 | 脚本路径 | 功能描述 | 调用方式 |
|---------|---------|---------|---------|
| create_skill.py | scripts/create_skill.py | 主创建工具：创建符合OpenCode规范的新技能，自动生成requirements.txt | `python scripts/create_skill.py <技能名> <描述> [选项]` |
| skill_fixer.py | scripts/skill_fixer.py | 主诊断修复工具：完整扫描、诊断、修复、报告生成 | `python scripts/skill_fixer.py [选项]` |
| version_manager.py | scripts/version_manager.py | 版本管理工具：更新版本号、递增版本、记录变更日志 | `python scripts/version_manager.py --skill <名称> --version <版本> --message <日志>` |
| safe_fix.py | scripts/safe_fix.py | 安全修复工具：智能检测避免重复修复 | `python scripts/safe_fix.py [技能目录]` |
| quick_fix.py | scripts/quick_fix.py | 快速修复工具：仅修复缺失YAML front matter | `python scripts/quick_fix.py [技能目录]` |

### 使用方法
[详细的使用说明，包括示例代码]
## 输出标准

### 创建技能时的输出
- 标准目录结构：`技能名/SKILL.md`、`技能名/config/` 和 `技能名/scripts/`
- 规范的SKILL.md文件，包含完整的YAML front matter和脚本索引
- 所有文件使用UTF-8编码
- config 目录下会创建一个 config.example.json 示例配置文件

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
- [ ] config目录已创建（用于存放配置文件）
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

**脚本执行规则验证**：
- [ ] SKILL.md中的调用方式使用绝对路径
- [ ] 脚本内部使用 `os.getcwd()` 获取输出目录
- [ ] 脚本不使用 `os.path.dirname(__file__)` 确定输出路径

### 技能依赖声明规则
当新技能需要使用其他已有技能的功能时，可以声明对其他技能的依赖，避免重复开发。

**声明格式**：
在 SKILL.md 的 YAML front matter 中使用 `depends` 字段声明依赖：

```yaml
---
name: my-skill
description: "技能描述"
depends:
  - skill: skill-name
    min_version: "1.0.0"
license: MIT License (见仓库根目录 LICENSE 文件)
---
```

**依赖字段说明**：
| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `skill` | string | 是 | 依赖的技能名称 |
| `min_version` | string | 否 | 最低版本号（语义化版本格式） |

**使用示例**：
```yaml
depends:
  - skill: email-sender
    min_version: "1.2.0"
  - skill: xlsx
    min_version: "1.0.0"
```

**创建技能时声明依赖**：
```bash
# 格式: 技能名:最低版本 或 技能名
python scripts/create_skill.py my-new-skill "描述" --skill-deps email-sender:1.0.0 xlsx
```

**注意事项**：
- 声明依赖后，可以在脚本中通过 subprocess 调用依赖技能的脚本
- 建议使用绝对路径调用
- 依赖检查应在脚本运行时进行，确保版本兼容

## 类别
开发工具、技能创建、规范验证、技能修复、系统维护
