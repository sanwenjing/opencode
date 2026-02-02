# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import chardet
import re
from pathlib import Path

def detect_encoding(text_bytes):
    """检测文本字节编码"""
    try:
        result = chardet.detect(text_bytes)
        return result['encoding'], result['confidence']
    except:
        return None, 0

def convert_filename(filename):
    """尝试转换文件名编码"""
    # 如果文件名已经是正常的UTF-8，直接返回
    try:
        filename.encode('utf-8').decode('utf-8')
        if not any(ord(c) > 127 and c in '�' for c in filename):
            return filename, None
    except:
        pass
    
    # 获取原始字节
    try:
        # 尝试从各种可能的编码转换
        original_bytes = filename.encode('latin1')
        
        # 常见的中文编码尝试顺序
        encodings_to_try = [
            'gbk', 'gb2312', 'gb18030', 'big5', 'utf-8', 
            'cp936', 'cp950', 'shift_jis', 'euc_jp'
        ]
        
        for encoding in encodings_to_try:
            try:
                decoded = original_bytes.decode(encoding)
                # 检查解码结果是否包含中文字符且没有乱码
                if '\u4e00' <= decoded <= '\u9fff' or '\u3400' <= decoded <= '\u4dbf':
                    # 检查是否还有替换字符
                    if '�' not in decoded:
                        return decoded, encoding
            except (UnicodeDecodeError, UnicodeEncodeError):
                continue
                
    except Exception as e:
        print(f"转换错误: {e}")
    
    return filename, None

def analyze_directory(directory="."):
    """分析目录中的文件"""
    print(f"正在分析目录: {os.path.abspath(directory)}")
    print("=" * 80)
    
    files_to_rename = []
    audio_extensions = {'.mp3', '.wma', '.wav', '.flac', '.m4a', '.ogg'}
    
    for filename in os.listdir(directory):
        file_path = Path(directory) / filename
        
        if file_path.is_file() and file_path.suffix.lower() in audio_extensions:
            # 检查是否包含乱码字符
            if '�' in filename or any(ord(c) > 127 and c in filename for c in filename):
                converted_name, detected_encoding = convert_filename(filename)
                
                if converted_name != filename:
                    files_to_rename.append({
                        'original': filename,
                        'converted': converted_name,
                        'encoding': detected_encoding
                    })
                    print(f"发现乱码文件:")
                    print(f"  原文件名: {filename}")
                    print(f"  转换后:   {converted_name}")
                    print(f"  检测编码: {detected_encoding}")
                    print("-" * 40)
    
    print(f"\n总共发现 {len(files_to_rename)} 个需要修复的文件")
    return files_to_rename

if __name__ == "__main__":
    # 检测chardet是否安装
    try:
        import chardet
    except ImportError:
        print("正在安装chardet库...")
        os.system(f"{sys.executable} -m pip install chardet")
        import chardet
    
    files_to_fix = analyze_directory()
    
    if files_to_fix:
        print("\n要执行重命名吗？(y/n)")
        response = input().strip().lower()
        if response == 'y':
            print("创建重命名脚本...")
            with open('rename_files.py', 'w', encoding='utf-8') as f:
                f.write("""# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os

files_to_rename = """ + str(files_to_fix) + """

for file_info in files_to_rename:
    try:
        old_path = file_info['original']
        new_path = file_info['converted']
        
        if os.path.exists(old_path) and not os.path.exists(new_path):
            os.rename(old_path, new_path)
            print(f"重命名成功: {old_path} -> {new_path}")
        else:
            print(f"跳过: {old_path} (文件不存在或目标已存在)")
    except Exception as e:
        print(f"重命名失败 {old_path}: {e}")

print("重命名操作完成！")
""")
            print("重命名脚本已创建为 'rename_files.py'")
            print("请运行该脚本执行重命名操作: python rename_files.py")
    else:
        print("没有发现需要修复的文件")