# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
from pathlib import Path

def fix_filenames_directly():
    """直接修复文件名"""
    print("直接修复音频文件名编码问题")
    print("=" * 50)
    
    directory = Path('.')
    audio_extensions = {'.mp3', '.wma', '.wav', '.flac', '.m4a', '.ogg'}
    fixed_count = 0
    error_count = 0
    
    for item in directory.iterdir():
        if item.is_file() and item.suffix.lower() in audio_extensions:
            original_name = item.name
            
            # 检查是否包含乱码字符
            if '�' in original_name:
                print(f"发现乱码文件: {original_name}")
                
                # 尝试修复
                fixed_name = try_fix_filename(original_name)
                
                if fixed_name != original_name:
                    try:
                        # 检查目标文件是否已存在
                        target_path = item.parent / fixed_name
                        if not target_path.exists():
                            item.rename(fixed_name)
                            print(f"  ✓ 修复成功: {fixed_name}")
                            fixed_count += 1
                        else:
                            print(f"  ✗ 目标文件已存在: {fixed_name}")
                            error_count += 1
                    except Exception as e:
                        print(f"  ✗ 修复失败: {e}")
                        error_count += 1
                else:
                    print(f"  - 无法自动修复")
                    error_count += 1
    
    print(f"\n修复完成!")
    print(f"成功修复: {fixed_count} 个文件")
    print(f"修复失败: {error_count} 个文件")

def try_fix_filename(filename):
    """尝试修复文件名"""
    if '�' not in filename:
        return filename
    
    # 方法1: 从latin1字节转换
    try:
        latin1_bytes = filename.encode('latin1', errors='ignore')
        for encoding in ['gbk', 'gb2312', 'gb18030', 'cp936', 'big5']:
            try:
                fixed = latin1_bytes.decode(encoding)
                if any('\u4e00' <= c <= '\u9fff' for c in fixed) and '�' not in fixed:
                    return fixed
            except:
                continue
    except:
        pass
    
    # 方法2: 尝试其他编码组合
    encodings_to_try = [
        ('utf-8', 'latin1'),
        ('cp1252', 'gbk'),
        ('gbk', 'utf-8'),
        ('latin1', 'cp1252')
    ]
    
    for enc1, enc2 in encodings_to_try:
        try:
            bytes_data = filename.encode(enc1, errors='ignore')
            fixed = bytes_data.decode(enc2, errors='ignore')
            if any('\u4e00' <= c <= '\u9fff' for c in fixed) and '�' not in fixed:
                return fixed
        except:
            continue
    
    return filename

if __name__ == "__main__":
    fix_filenames_directly()