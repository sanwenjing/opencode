# 智能重复文件清理技能使用说明

## 📋 概述
这是一个专门为音乐文件设计的智能重复文件清理工具，具有以下特点：
- ✅ 绝对保护含中文字符的文件
- 🎯 智能识别有意义英文文件名  
- 🔒 MD5校验确保文件内容完全相同
- 👀 安全的预览和执行机制

## 🚀 快速开始

### 1. 预览模式（推荐先执行）
```bash
python duplicate_cleaner_final.py
# 或指定目录
python duplicate_cleaner_final.py /path/to/music
```

### 2. 执行删除模式
```bash
python duplicate_cleaner_final.py --execute
# 或指定目录
python duplicate_cleaner_final.py /path/to/music --execute
```

## 📚 API 使用方式

### 基础API

```python
from duplicate_cleaner_final import preview_duplicate_cleanup, execute_duplicate_cleanup

# 预览重复文件
result = preview_duplicate_cleanup('.')
print(f"发现 {result['total_files']} 个重复文件")

# 执行清理
result = execute_duplicate_cleanup('.')
print(f"删除了 {result['deleted_count']} 个文件")
```

### 高级API

```python
from duplicate_cleaner_final import clean_duplicate_files

# 预览模式
preview = clean_duplicate_files('.', dry_run=True)

# 执行模式
cleanup = clean_duplicate_files('.', dry_run=False)
```

## 🛡️ 安全策略

### 文件优先级（从高到低）
1. **中文文件** - 包含中文字符的文件，绝对不删除
2. **有意义英文** - 包含歌手名、歌曲名等有意义的英文
3. **普通英文** - 其他英文名称
4. **编码文件** - 以下划线开头的随机字符串文件

### 保护机制
- 双重检查中文文件，绝不删除
- MD5校验确保删除的文件内容完全相同
- 预览模式让用户确认后再执行

## 📊 输出示例

### 预览输出
```
=== 重复文件清理预览 ===

=== 大小: 3354777 字节 (3.20 MB) ===
MD5: 265582ad...
  [保留] 梁静茹 - 勇气.mp3 (包含中文字符)
  [删除] 梁静茹 - 宁夏.mp3 (包含中文字符)
  [删除] 王心凌 - 爱你.mp3 (包含中文字符)
  [删除] 许绍洋 - 花香.mp3 (包含中文字符)
  [删除] _0RM7TT.MP3 (编码文件)
  [删除] _0T0LX4.MP3 (编码文件)
  [删除] _P6PAI7.MP3 (编码文件)
  [删除] _UICPDX.MP3 (编码文件)
  [空间] 可释放空间: 22.40 MB

=== 总结 ===
发现 145 个重复文件
可释放空间: 612.75 MB
保护策略: 绝对保护中文文件
```

### 执行输出
```
=== 开始执行清理 ===

[删除] _0RM7TT.MP3
[删除] _0T0LX4.MP3
[删除] _P6PAI7.MP3
[保护] 中文文件: 梁静茹 - 宁夏.mp3
[保护] 中文文件: 王心凌 - 爱你.mp3
...

=== 清理完成 ===
成功删除: 127 个文件
保护文件: 17 个
释放空间: 537.48 MB
```

## ⚙️ 返回数据格式

### 预览结果
```python
{
    'groups': [...],           # 重复文件组详情
    'total_files': 145,       # 重复文件总数
    'total_space_mb': 612.75, # 可释放空间(MB)
    'group_count': 89         # 重复文件组数
}
```

### 清理结果
```python
{
    'success': True,               # 是否成功
    'deleted_count': 127,          # 删除文件数
    'protected_count': 17,          # 保护文件数
    'failed_count': 0,             # 失败文件数
    'freed_space_mb': 537.48       # 实际释放空间(MB)
}
```

## 🔧 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `directory` | 要清理的目录路径 | `/music` |
| `--execute` | 执行实际删除 | `--execute` |

## 📝 注意事项

1. **备份重要文件** - 虽然有保护机制，但建议先备份
2. **预览优先** - 建议先运行预览模式确认结果
3. **权限检查** - 确保对目标目录有读写权限
4. **网络位置** - 不建议直接操作网络共享文件夹

## 🎵 适用场景

- 🎶 音乐库重复文件清理
- 📁 多来源合并的文件整理
- 🔧 自动化存储空间优化
- 📊 文件系统维护和清理

## 🔄 更新历史

- **v1.0** - 初始版本，支持智能重复文件清理
- 支持MD5校验、中文保护、优先级排序
- 提供预览和执行两种模式
- 完整的API接口和命令行支持

---

## 📞 技术支持

如有问题或建议，请检查：
1. Python版本是否为3.6+
2. 目标目录是否存在
3. 是否有足够的磁盘空间
4. 文件权限是否正确

**安全提示**: 本工具会永久删除文件，请谨慎使用！