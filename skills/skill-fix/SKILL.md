---
name: skill-fix
description: "技能工具 - 专业的技能工具"
license: 专有。LICENSE.txt 包含完整条款
---

---
name: skill-fix
description: "---
name: skill-fix
description: "专门用于修复技能加载问题的全局诊断和修复工具。当 Claude 需要修复技能系统时用于：(1) 诊断技能加载问题，(2) 修复 YAML front matter 缺失，(3) 规范化技能格式，(4) 清理技能缓存，(5) 验证技能完整性，或 (6) 重新加载技能系统"
license: 专有。LICENSE.txt 包含完整条款
---

 技能修复工具

 描述
专门用于修复技能系统中各类加载和配置问题的诊断和修复工具。此技能能够自动识别常见的技能问题并提供标准化修复方案。

 功能
- **智能诊断**: 自动识别技能加载问题的根本原因
- **YAML Front Matter 修复**: 自动添加或修正缺失的技能元数据
- **格式标准化**: 确保所有技能文件符合统一的格式规范
- **缓存清理**: 清除可能影响技能加载的缓存文件
- **完整性验证**: 验证技能结构和依赖关系的完整性
- **批量修复**: 支持对多个技能进行批量问题修复

 诊断流程

 1. 问题检测
```python
def diagnose_skill_system():
    """
    全面诊断技能系统状态
    """
    issues = []
    
     检查技能目录
    skill_dirs = scan_skill_directories()
    for skill_dir in skill_dirs:
        issues.extend(check_skill_directory(skill_dir))
    
     检查系统配置
    issues.extend(check_system_configuration())
    
     检查缓存状态
    issues.extend(check_cache_status())
    
    return categorize_issues(issues)
```

 2. 常见问题识别

 缺失 YAML Front Matter
- **症状**: 技能目录存在但无法加载
- **检测**: SKILL.md 文件缺少 `---` 包围的 YAML 头部
- **修复**: 自动生成标准化的 front matter

 技能名称不匹配
- **症状**: 目录名与 YAML 中的 name 字段不一致
- **检测**: 比较目录名和 YAML name 字段
- **修复**: 统一使用目录名作为标准名称

 许可证信息缺失
- **症状**: 缺少 license 字段或不规范的许可证声明
- **检测**: 检查 YAML 中的 license 字段
- **修复**: 添加标准许可证声明

 文件权限问题
- **症状**: 技能文件无法读取或访问
- **检测**: 检查文件权限和所有者
- **修复**: 修正文件权限设置

 修复操作

 自动修复模式
```bash
 修复所有发现的技能问题
python skill_fixer.py --auto-fix

 仅修复特定技能
python skill_fixer.py --skill skill_name --fix

 仅诊断不修复
python skill_fixer.py --diagnose-only
```

 手动修复指导
```python
def generate_fix_instructions(skill_path, issue_type):
    """
    为特定问题生成详细修复指导
    """
    instructions = {
        'missing_yaml': generate_yaml_fix_instructions(skill_path),
        'name_mismatch': generate_name_fix_instructions(skill_path),
        'license_missing': generate_license_fix_instructions(skill_path),
        'corrupted_files': generate_recovery_instructions(skill_path)
    }
    return instructions.get(issue_type, generic_fix_instructions())
```

 预防性维护

 技能验证检查清单
- [ ] YAML front matter 完整且格式正确
- [ ] name 字段与目录名一致
- [ ] description 字段符合规范（包含使用场景）
- [ ] license 字段存在且有效
- [ ] SKILL.md 文件编码为 UTF-8
- [ ] 没有语法错误或格式问题
- [ ] 依赖文件和脚本完整

 定期维护建议
1. **每周扫描**: 运行完整的技能系统诊断
2. **新增技能验证**: 新增技能后立即验证格式
3. **版本控制跟踪**: 跟踪技能文件的变更历史
4. **备份策略**: 定期备份技能配置文件

 使用方法

 快速修复
```bash
 自动修复所有技能问题
skill-fix --auto --verbose

 修复特定技能
skill-fix --target duplicate_file_cleaner --fix-yaml
```

 交互式修复
```bash
 启动交互式修复向导
skill-fix --interactive

 逐步指导修复过程
skill-fix --step-by-step --skill problem_skill
```

 批量操作
```bash
 批量添加缺失的 YAML front matter
skill-fix --batch --add-yaml

 批量标准化技能描述格式
skill-fix --batch --normalize-descriptions
```

 高级功能

 技能模板生成
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

 {skill_name.replace('-', ' ').title()} 技能

 描述
{description}

 功能
- **功能1**: 详细描述
- **功能2**: 详细描述

 使用方法

 基本用法
```bash
 基本命令示例
command_example
```

 编程接口
```python
 Python API 示例
from {skill_name} import main_function

result = main_function(parameters)
```

 参数
- `param1` (类型): 参数描述
- `param2` (类型): 参数描述

 输出
返回内容包括：
- 结果描述
- 数据格式说明
- 错误处理信息

 类别
技能分类1，技能分类2
"""
    return template
```

 备份和恢复
```python
def backup_skill_configuration():
    """备份当前技能配置"""
    pass

def restore_skill_configuration(backup_file):
    """从备份恢复技能配置"""
    pass
```

 故障排除

 常见错误代码
- **SKILL001**: YAML front matter 缺失
- **SKILL002**: 技能名称不匹配
- **SKILL003**: 许可证信息无效
- **SKILL004**: 文件编码问题
- **SKILL005**: 依赖文件缺失

 调试模式
```bash
 启用详细调试日志
skill-fix --debug --log-file skill_fix.log

 显示详细的修复过程
skill-fix --verbose --step-by-step
```

 类别
系统工具，维护修复，诊断工具 - 专业的技能工具，用于..."
license: 专有。LICENSE.txt 包含完整条款
---

---
name: skill-fix
description: "专门用于修复技能加载问题的全局诊断和修复工具。当 Claude 需要修复技能系统时用于：(1) 诊断技能加载问题，(2) 修复 YAML front matter 缺失，(3) 规范化技能格式，(4) 清理技能缓存，(5) 验证技能完整性，或 (6) 重新加载技能系统"
license: 专有。LICENSE.txt 包含完整条款
---

# 技能修复工具

## 描述
专门用于修复技能系统中各类加载和配置问题的诊断和修复工具。此技能能够自动识别常见的技能问题并提供标准化修复方案。

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

## 修复操作

### 自动修复模式
```bash
# 修复所有发现的技能问题
python skill_fixer.py --auto-fix

# 仅修复特定技能
python skill_fixer.py --skill skill_name --fix

# 仅诊断不修复
python skill_fixer.py --diagnose-only
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

### 定期维护建议
1. **每周扫描**: 运行完整的技能系统诊断
2. **新增技能验证**: 新增技能后立即验证格式
3. **版本控制跟踪**: 跟踪技能文件的变更历史
4. **备份策略**: 定期备份技能配置文件

## 使用方法

### 快速修复
```bash
# 自动修复所有技能问题
skill-fix --auto --verbose

# 修复特定技能
skill-fix --target duplicate_file_cleaner --fix-yaml
```

### 交互式修复
```bash
# 启动交互式修复向导
skill-fix --interactive

# 逐步指导修复过程
skill-fix --step-by-step --skill problem_skill
```

### 批量操作
```bash
# 批量添加缺失的 YAML front matter
skill-fix --batch --add-yaml

# 批量标准化技能描述格式
skill-fix --batch --normalize-descriptions
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

## 功能
- **功能1**: 详细描述
- **功能2**: 详细描述

## 使用方法

### 基本用法
```bash
# 基本命令示例
command_example
```

### 编程接口
```python
# Python API 示例
from {skill_name} import main_function

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

### 调试模式
```bash
# 启用详细调试日志
skill-fix --debug --log-file skill_fix.log

# 显示详细的修复过程
skill-fix --verbose --step-by-step
```

## 类别
系统工具，维护修复，诊断工具