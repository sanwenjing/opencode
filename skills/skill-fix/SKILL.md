---
name: skill-fix
description: "专门用于修复技能加载问题的全局诊断和修复工具。当 Claude 需要修复技能系统时用于：(1) 诊断技能加载问题，(2) 修复 YAML front matter 缺失，(3) 规范化技能格式，(4) 清理技能缓存，(5) 验证技能完整性，或 (6) 重新加载技能系统"
license: 专有。LICENSE.txt 包含完整条款
---

# 技能修复工具

## 描述
专门用于修复技能系统中各类加载和配置问题的诊断和修复工具。此技能能够自动识别常见的技能问题并提供标准化修复方案。

## 目录结构
```
skill-fix/
├── SKILL.md              # 技能主配置文件（当前文件）
└── scripts/              # 脚本目录（存放所有诊断和修复脚本）
    ├── diagnose.py       # 诊断脚本：检测技能系统问题（位于 scripts/diagnose.py）
    ├── fix_yaml.py       # YAML修复脚本：修复front matter问题（位于 scripts/fix_yaml.py）
    ├── fix_structure.py  # 结构修复脚本：修复目录结构问题（位于 scripts/fix_structure.py）
    └── validator.py      # 验证脚本：验证技能完整性（位于 scripts/validator.py）
```

## 脚本索引
**编码声明**: 本技能所有脚本默认使用UTF-8编码，Windows系统下已配置UTF-8控制台输出。

| 脚本名称 | 脚本路径 | 功能描述 | 调用方式 |
|---------|---------|---------|---------|
| diagnose.py | scripts/diagnose.py | 全面诊断技能系统状态，检测各类问题 | `python scripts/diagnose.py` |
| fix_yaml.py | scripts/fix_yaml.py | 修复YAML front matter缺失或格式问题 | `python scripts/fix_yaml.py --skill <name>` |
| fix_structure.py | scripts/fix_structure.py | 修复目录结构问题，创建缺失的scripts目录 | `python scripts/fix_structure.py --skill <name>` |
| validator.py | scripts/validator.py | 验证技能完整性和规范性 | `python scripts/validator.py --skill <name>` |

## 功能
- **智能诊断**: 自动识别技能加载问题的根本原因
- **YAML Front Matter 修复**: 自动添加或修正缺失的技能元数据
- **格式标准化**: 确保所有技能文件符合统一的格式规范
- **缓存清理**: 清除可能影响技能加载的缓存文件
- **完整性验证**: 验证技能结构和依赖关系的完整性
- **批量修复**: 支持对多个技能进行批量问题修复

## 诊断流程

### 1. 问题检测
```python
def diagnose_skill_system():
    """
    全面诊断技能系统状态
    """
    issues = []
    
    # 检查技能目录
    skill_dirs = scan_skill_directories()
    for skill_dir in skill_dirs:
        issues.extend(check_skill_directory(skill_dir))
    
    # 检查系统配置
    issues.extend(check_system_configuration())
    
    # 检查缓存状态
    issues.extend(check_cache_status())
    
    return categorize_issues(issues)
```

### 2. 常见问题识别

#### 缺失 YAML Front Matter
- **症状**: 技能目录存在但无法加载
- **检测**: SKILL.md 文件缺少 `---` 包围的 YAML 头部
- **修复**: 自动生成标准化的 front matter

#### 技能名称不匹配
- **症状**: 目录名与 YAML 中的 name 字段不一致
- **检测**: 比较目录名和 YAML name 字段
- **修复**: 统一使用目录名作为标准名称

#### 许可证信息缺失
- **症状**: 缺少 license 字段或不规范的许可证声明
- **检测**: 检查 YAML 中的 license 字段
- **修复**: 添加标准许可证声明

#### 文件权限问题
- **症状**: 技能文件无法读取或访问
- **检测**: 检查文件权限和所有者
- **修复**: 修正文件权限设置

#### 脚本位置或索引缺失（新增检查项）
- **症状**: SKILL.md 缺少脚本索引章节或目录结构说明
- **检测**: 检查文档中是否包含：
  - 目录结构章节（说明文件组织方式）
  - 脚本索引表格（列出所有脚本的路径和调用方式）
  - 编码声明（声明所有脚本使用UTF-8编码）
- **修复**: 自动添加标准的脚本索引章节

#### UTF-8编码问题（新增检查项）
- **症状**: 脚本文件编码非UTF-8，导致中文显示乱码
- **检测**: 检查脚本文件编码和BOM标记
- **修复**: 转换编码为UTF-8，确保无BOM

## 修复操作

### 自动修复模式
```bash
# 修复所有发现的技能问题
python scripts/fix_yaml.py --auto-fix

# 仅修复特定技能
python scripts/fix_structure.py --skill skill_name

# 仅诊断不修复
python scripts/diagnose.py --diagnose-only
```

### 手动修复指导
```python
def generate_fix_instructions(skill_path, issue_type):
    """
    为特定问题生成详细修复指导
    """
    instructions = {
        'missing_yaml': generate_yaml_fix_instructions(skill_path),
        'name_mismatch': generate_name_fix_instructions(skill_path),
        'license_missing': generate_license_fix_instructions(skill_path),
        'missing_script_index': generate_script_index_instructions(skill_path),
        'utf8_encoding_error': generate_utf8_fix_instructions(skill_path),
        'corrupted_files': generate_recovery_instructions(skill_path)
    }
    return instructions.get(issue_type, generic_fix_instructions())
```

## 预防性维护

### 技能验证检查清单
- [ ] YAML front matter 完整且格式正确
- [ ] name 字段与目录名一致
- [ ] description 字段符合规范（包含使用场景）
- [ ] license 字段存在且有效
- [ ] SKILL.md 文件编码为 UTF-8
- [ ] 没有语法错误或格式问题
- [ ] 依赖文件和脚本完整
- [ ] **目录结构说明**: SKILL.md 包含目录结构章节，说明文件组织方式
- [ ] **脚本索引完整**: SKILL.md 包含脚本索引表格，列出所有脚本的路径和调用方式
- [ ] **编码声明**: SKILL.md 明确声明所有脚本使用UTF-8编码
- [ ] **脚本位置正确**: 所有脚本存放在scripts目录下，不在根目录

### 定期维护建议
1. **每周扫描**: 运行完整的技能系统诊断
2. **新增技能验证**: 新增技能后立即验证格式
3. **版本控制跟踪**: 跟踪技能文件的变更历史
4. **备份策略**: 定期备份技能配置文件
5. **编码检查**: 定期检查脚本文件编码，确保为UTF-8

## 使用方法

### 快速修复
```bash
# 自动修复所有技能问题
python scripts/fix_yaml.py --auto --verbose

# 修复特定技能
python scripts/fix_structure.py --target duplicate_file_cleaner --fix-yaml

# 诊断特定技能
python scripts/diagnose.py --skill problem_skill
```

### 交互式修复
```bash
# 启动交互式修复向导
python scripts/fix_yaml.py --interactive

# 逐步指导修复过程
python scripts/fix_structure.py --step-by-step --skill problem_skill
```

### 批量操作
```bash
# 批量添加缺失的 YAML front matter
python scripts/fix_yaml.py --batch --add-yaml

# 批量标准化技能描述格式
python scripts/fix_yaml.py --batch --normalize-descriptions

# 批量修复脚本索引缺失
python scripts/validator.py --batch --fix-script-index

# 批量转换编码为UTF-8
python scripts/fix_yaml.py --batch --fix-encoding
```

## 新增修复功能：脚本索引和编码检查

### 脚本索引修复
当检测到SKILL.md缺少脚本索引时，自动添加标准格式的脚本索引章节：

```markdown
### 脚本索引
**编码声明**: 本技能所有脚本默认使用UTF-8编码，Windows系统下已配置UTF-8控制台输出。

| 脚本名称 | 脚本路径 | 功能描述 | 调用方式 |
|---------|---------|---------|---------|
| script1.py | scripts/script1.py | 功能描述1 | `python scripts/script1.py` |
| script2.py | scripts/script2.py | 功能描述2 | `python scripts/script2.py` |
```

### UTF-8编码修复
```python
def fix_utf8_encoding(file_path):
    """
    修复文件编码为UTF-8
    """
    # 检测当前编码
    current_encoding = detect_encoding(file_path)
    
    # 读取文件内容
    with open(file_path, 'r', encoding=current_encoding, errors='ignore') as f:
        content = f.read()
    
    # 以UTF-8编码写回
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 如果是Python脚本，添加UTF-8控制台编码设置
    if file_path.endswith('.py'):
        add_utf8_console_setup(file_path)

def add_utf8_console_setup(file_path):
    """
    为Python脚本添加UTF-8控制台编码设置
    """
    utf8_setup = '''# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

'''
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已存在编码设置
    if 'sys.stdout = io.TextIOWrapper' not in content:
        # 在文件开头添加（跳过shebang和现有注释）
        lines = content.split('\n')
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('#'):
                insert_idx = i + 1
            elif line.strip() == '':
                continue
            else:
                break
        
        lines.insert(insert_idx, utf8_setup)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
```

### 目录结构修复
```python
def fix_directory_structure(skill_path):
    """
    修复技能目录结构
    """
    # 创建scripts目录（如果不存在）
    scripts_dir = os.path.join(skill_path, 'scripts')
    if not os.path.exists(scripts_dir):
        os.makedirs(scripts_dir)
        print(f"创建目录: {scripts_dir}")
    
    # 移动根目录下的脚本文件到scripts目录
    for item in os.listdir(skill_path):
        item_path = os.path.join(skill_path, item)
        if os.path.isfile(item_path) and item.endswith(('.py', '.sh', '.js', '.bat')):
            if item != 'SKILL.md':
                target_path = os.path.join(scripts_dir, item)
                shutil.move(item_path, target_path)
                print(f"移动文件: {item} -> scripts/{item}")
```

## 高级功能

### 技能模板生成
```python
def generate_skill_template(skill_name, description):
    """
    生成标准化的技能模板文件
    """
    template = f"""---
name: {skill_name}
description: "{description}"
license: 专有。LICENSE.txt 包含完整条款
---

# {skill_name.replace('-', ' ').title()} 技能

## 描述
{description}

## 目录结构
```
{skill_name}/
├── SKILL.md              # 技能主配置文件
└── scripts/              # 脚本目录（存放所有脚本）
    └── main.py          # 主执行脚本（位于 scripts/main.py）
```

## 脚本索引
**编码声明**: 本技能所有脚本默认使用UTF-8编码，Windows系统下已配置UTF-8控制台输出。

| 脚本名称 | 脚本路径 | 功能描述 | 调用方式 |
|---------|---------|---------|---------|
| main.py | scripts/main.py | 主程序入口 | `python scripts/main.py` |

## 功能
- **功能1**: 详细描述
- **功能2**: 详细描述

## 使用方法

### 基本用法
```bash
# 基本命令示例
python scripts/main.py --help
```

### 编程接口
```python
# Python API 示例
from scripts.main import main_function

result = main_function(parameters)
```

## 参数
- `param1` (类型): 参数描述
- `param2` (类型): 参数描述

## 输出
返回内容包括：
- 结果描述
- 数据格式说明
- 错误处理信息

## 类别
技能分类1，技能分类2
"""
    return template
```

### 备份和恢复
```python
def backup_skill_configuration():
    """备份当前技能配置"""
    pass

def restore_skill_configuration(backup_file):
    """从备份恢复技能配置"""
    pass
```

## 故障排除

### 常见错误代码
- **SKILL001**: YAML front matter 缺失
- **SKILL002**: 技能名称不匹配
- **SKILL003**: 许可证信息无效
- **SKILL004**: 文件编码问题
- **SKILL005**: 依赖文件缺失
- **SKILL006**: 脚本索引缺失（新增）
- **SKILL007**: 目录结构不正确（新增）
- **SKILL008**: UTF-8编码声明缺失（新增）

### 调试模式
```bash
# 启用详细调试日志
python scripts/diagnose.py --debug --log-file skill_fix.log

# 显示详细的修复过程
python scripts/fix_yaml.py --verbose --step-by-step

# 仅检查脚本索引和编码
python scripts/validator.py --check-script-index --check-encoding
```

## 类别
系统工具，维护修复，诊断工具
