"""
智能重复文件清理技能 (Intelligent Duplicate File Cleaner Skill)

专门用于音乐文件重复清理的标准化工具，具备以下特性：
- 绝对保护含中文字符的文件
- 智能识别有意义英文文件名
- MD5校验确保文件内容完全相同
- 安全的预览和执行机制

使用方法：
1. preview_duplicate_cleanup('.') - 预览重复文件
2. execute_duplicate_cleanup('.') - 执行清理操作

作者: Claude Assistant
版本: 1.0
"""

import os
import hashlib
import re
import sys

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class DuplicateFileCleaner:
    """智能重复文件清理工具"""
    
    def __init__(self):
        self.files_by_size = {}
        self.files_to_delete = []
        self.protected_count = 0
        
    def _calculate_md5(self, filepath):
        """计算文件MD5"""
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (OSError, IOError):
            return None
    
    def _has_chinese(self, filename):
        """检查是否含中文字符"""
        return bool(re.search(r'[\u4e00-\u9fff]', os.path.basename(filename)))
    
    def _is_meaningful(self, filename):
        """判断文件名是否有意义"""
        basename = os.path.basename(filename)
        
        if self._has_chinese(filename):
            return True, "包含中文字符"
        
        if basename.startswith('_'):
            return False, "编码文件"
        
        # 英文模式识别
        patterns = [
            r'\b(singer|song|music|love|heart|you|me|the|and|for|with|my|your)\b',
            r'\b(jacky|andy|leon|aaron|faye|sammi|kelly|joey|eason|jay)\b',
            r'\b(coldplay|maroon|greenday|linkin|bon|jovi|beyond|taylor|swift)\b',
            r'[a-zA-Z]{4,}'
        ]
        
        for pattern in patterns:
            if re.search(pattern, basename, re.IGNORECASE):
                return True, "有意义英文"
        
        return False, "无特殊标记"
    
    def _sort_priority(self, filepath):
        """文件优先级排序"""
        basename = os.path.basename(filepath)
        is_meaningful, _ = self._is_meaningful(filepath)
        
        if self._has_chinese(filepath):
            return (0, basename.lower())
        elif is_meaningful and not basename.startswith('_'):
            return (1, basename.lower())
        elif not basename.startswith('_'):
            return (2, basename.lower())
        else:
            return (3, basename.lower())
    
    def scan_and_analyze(self, directory='.'):
        """扫描并分析重复文件"""
        print("正在扫描目录中...")
        
        # 扫描文件
        for root, dirs, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    size = os.path.getsize(filepath)
                    if size not in self.files_by_size:
                        self.files_by_size[size] = []
                    self.files_by_size[size].append(filepath)
                except (OSError, IOError):
                    pass
        
        # 分析重复文件
        duplicate_groups = []
        total_space = 0
        duplicate_count = 0
        
        for size, file_list in self.files_by_size.items():
            if len(file_list) > 1:
                # MD5分组
                md5_groups = {}
                for filepath in file_list:
                    md5_hash = self._calculate_md5(filepath)
                    if md5_hash:
                        if md5_hash not in md5_groups:
                            md5_groups[md5_hash] = []
                        md5_groups[md5_hash].append(filepath)
                
                # 找重复组
                for md5_hash, files in md5_groups.items():
                    if len(files) > 1:
                        sorted_files = sorted(files, key=self._sort_priority)
                        keep_file = sorted_files[0]
                        delete_files = sorted_files[1:]
                        
                        duplicate_groups.append({
                            'size': size,
                            'size_mb': size / 1024 / 1024,
                            'md5': md5_hash,
                            'keep_file': keep_file,
                            'delete_files': delete_files,
                            'space_freed': len(delete_files) * size
                        })
                        
                        self.files_to_delete.extend(delete_files)
                        total_space += len(delete_files) * size
                        duplicate_count += len(delete_files)
        
        return {
            'groups': duplicate_groups,
            'total_files': duplicate_count,
            'total_space_mb': total_space / 1024 / 1024,
            'group_count': len(duplicate_groups)
        }
    
    def preview_cleanup(self, directory='.'):
        """预览清理操作"""
        print("=== 重复文件清理预览 ===\n")
        
        analysis = self.scan_and_analyze(directory)
        
        if not analysis['groups']:
            print("未发现重复文件")
            return analysis
        
        for group in analysis['groups']:
            print(f"=== 大小: {group['size']} 字节 ({group['size_mb']:.2f} MB) ===")
            print(f"MD5: {group['md5'][:8]}...")
            
            keep_basename = os.path.basename(group['keep_file'])
            _, keep_reason = self._is_meaningful(group['keep_file'])
            print(f"  [保留] {keep_basename} ({keep_reason})")
            
            for delete_file in group['delete_files']:
                delete_basename = os.path.basename(delete_file)
                _, delete_reason = self._is_meaningful(delete_file)
                print(f"  [删除] {delete_basename} ({delete_reason})")
            
            print(f"  [空间] 可释放空间: {group['space_freed'] / 1024 / 1024:.2f} MB\n")
        
        print("=== 总结 ===")
        print(f"发现 {analysis['total_files']} 个重复文件")
        print(f"可释放空间: {analysis['total_space_mb']:.2f} MB")
        print(f"保护策略: 绝对保护中文文件")
        print(f"优先级: 中文 > 有意义英文 > 普通英文 > 编码文件")
        
        return analysis
    
    def execute_cleanup(self, directory='.'):
        """执行清理操作"""
        print("=== 开始执行清理 ===\n")
        
        if not self.files_to_delete:
            print("没有需要删除的文件")
            return {'success': False, 'message': '没有重复文件'}
        
        deleted_count = 0
        deleted_space = 0
        failed_count = 0
        protected_count = 0
        
        for filepath in self.files_to_delete:
            try:
                # 双重保护中文文件
                if self._has_chinese(filepath):
                    print(f"[保护] 中文文件: {os.path.basename(filepath)}")
                    protected_count += 1
                    continue
                
                file_size = os.path.getsize(filepath)
                os.remove(filepath)
                print(f"[删除] {os.path.basename(filepath)}")
                deleted_count += 1
                deleted_space += file_size
                
            except (OSError, IOError) as e:
                print(f"[失败] {os.path.basename(filepath)} - {e}")
                failed_count += 1
        
        print(f"\n=== 清理完成 ===")
        print(f"成功删除: {deleted_count} 个文件")
        if protected_count > 0:
            print(f"保护文件: {protected_count} 个")
        if failed_count > 0:
            print(f"失败文件: {failed_count} 个")
        print(f"释放空间: {deleted_space / 1024 / 1024:.2f} MB")
        
        return {
            'success': True,
            'deleted_count': deleted_count,
            'protected_count': protected_count,
            'failed_count': failed_count,
            'freed_space_mb': deleted_space / 1024 / 1024
        }

# ===== 公共API函数 =====

def preview_duplicate_cleanup(directory='.'):
    """
    预览重复文件清理操作
    
    Args:
        directory (str): 要清理的目录路径，默认为当前目录
    
    Returns:
        dict: 预览结果统计信息
    """
    cleaner = DuplicateFileCleaner()
    return cleaner.preview_cleanup(directory)

def execute_duplicate_cleanup(directory='.'):
    """
    执行重复文件清理操作
    
    Args:
        directory (str): 要清理的目录路径，默认为当前目录
    
    Returns:
        dict: 清理结果统计信息
    """
    cleaner = DuplicateFileCleaner()
    
    # 先预览
    preview = cleaner.preview_cleanup(directory)
    
    if not preview['groups']:
        return preview
    
    # 再执行
    return cleaner.execute_cleanup(directory)

def clean_duplicate_files(directory='.', dry_run=True):
    """
    通用清理函数
    
    Args:
        directory (str): 要清理的目录路径
        dry_run (bool): True为预览，False为执行删除
    
    Returns:
        dict: 操作结果
    """
    cleaner = DuplicateFileCleaner()
    
    if dry_run:
        return cleaner.preview_cleanup(directory)
    else:
        cleaner.preview_cleanup(directory)  # 先显示预览
        return cleaner.execute_cleanup(directory)

# ===== 命令行接口 =====
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='智能重复文件清理工具')
    parser.add_argument('directory', nargs='?', default='.', help='要清理的目录路径')
    parser.add_argument('--execute', action='store_true', help='执行实际删除（默认为预览模式）')
    
    args = parser.parse_args()
    
    if args.execute:
        print("执行模式: 将实际删除文件")
        execute_duplicate_cleanup(args.directory)
    else:
        print("预览模式: 仅显示将要删除的文件")
        preview_duplicate_cleanup(args.directory)
        
        if len(sys.argv) > 1 and '--execute' not in sys.argv:
            print(f"\n要执行实际删除，请运行:")
            print(f"python {os.path.basename(__file__)} {args.directory} --execute")