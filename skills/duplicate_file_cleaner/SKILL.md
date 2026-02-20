---
name: duplicate_file_cleaner
description: 具有智能文件保护策略的综合重复文件清理工具。此技能专门识别和安全删除重复文件，同时为重要文件提供强大保护。当 Claude 需要清理重复文件时用于：(1)
  智能识别重复文件，(2) 保护重要文件，(3) 安全预览清理操作，(4) 执行批量删除，或 (5) 生成清理报告
license: MIT License (见仓库根目录 LICENSE 文件)
version: 1.0.0
---

# 重复文件清理技能

## 描述
具有智能文件保护策略的综合重复文件清理工具。此技能专门识别和安全删除重复文件，同时为重要文件提供强大保护。

## 功能
- **智能文件保护**：优先保护具有中文字符和有意义名称的文件
- **MD5 验证**：确保只删除相同内容的文件
- **安全预览模式**：执行前预览更改
- **全面 API**：编程和命令行接口
- **详细报告**：清理操作的完整日志和统计

## 脚本索引

| 脚本 | 描述 | 主要功能 |
|------|------|----------|
| `scripts/duplicate_cleaner_final.py` | 智能重复文件清理主程序 | 扫描、分析、预览和执行重复文件清理操作 |

## 使用方法

### 命令行
```bash
# 预览重复文件
python scripts/duplicate_cleaner_final.py /path/to/directory

# 执行清理
python scripts/duplicate_cleaner_final.py /path/to/directory --execute
```

### 编程方式
```python
from scripts.duplicate_cleaner_final import preview_duplicate_cleanup, execute_duplicate_cleanup

# 预览模式
result = preview_duplicate_cleanup('.')
print(f"发现 {result['total_files']} 个重复文件")

# 执行清理
result = execute_duplicate_cleanup('.')
print(f"删除了 {result['deleted_count']} 个文件")
```

## 参数
- `directory` (字符串)：目标目录路径（必需）
- `--execute` (布尔值)：执行实际删除的标志（可选，默认：预览模式）

## 保护策略
文件优先级保护：
1. 包含中文字符的文件（最高优先级）
2. 有意义英文名称的文件
3. 常规英文文件名
4. 系统生成/随机文件名（最低优先级）

## 输出
返回详细统计包括：
- 发现的重复文件数量
- 可释放的空间
- 被安全规则保护的文件
- 实际删除结果

## 类别
文件管理，系统工具