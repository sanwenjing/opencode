# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import subprocess
from pathlib import Path

def get_windows_dir_output():
    """获取Windows dir命令的输出"""
    try:
        result = subprocess.run(['cmd', '/c', 'dir', '/b'], 
                              capture_output=True, 
                              text=True, 
                              encoding='gbk',  # 尝试GBK编码
                              cwd='.')
        return result.stdout.splitlines()
    except Exception as e:
        print(f"获取Windows输出失败: {e}")
        return []

def fix_encoding_from_bytes(filename_str):
    """从字符串的字节表示修复编码"""
    try:
        # 尝试获取原始字节
        if isinstance(filename_str, str):
            # 尝试多种编码方式获取字节
            for encoding in ['gbk', 'gb2312', 'latin1', 'cp1252']:
                try:
                    byte_data = filename_str.encode(encoding)
                    # 尝试用UTF-8解码
                    decoded = byte_data.decode('utf-8')
                    if '\u4e00' <= decoded <= '\u9fff' and '�' not in decoded:
                        return decoded
                except:
                    continue
    except:
        pass
    
    return filename_str

def analyze_windows_filenames():
    """分析Windows命令行下的文件名"""
    print("获取Windows命令行文件列表...")
    windows_files = get_windows_dir_output()
    
    audio_extensions = ['.mp3', '.wma', '.wav', '.flac', '.m4a', '.ogg']
    problem_files = []
    
    for filename in windows_files:
        # 检查是否为音频文件
        if any(filename.lower().endswith(ext) for ext in audio_extensions):
            # 检查是否包含乱码字符
            if '�' in filename:
                print(f"发现乱码文件: {filename}")
                
                # 尝试修复
                fixed = fix_encoding_from_bytes(filename)
                if fixed != filename:
                    print(f"  修复后: {fixed}")
                    problem_files.append({
                        'original': filename,
                        'fixed': fixed
                    })
                else:
                    problem_files.append({
                        'original': filename,
                        'fixed': None
                    })
                print()
    
    return problem_files

def create_batch_rename_script(problem_files):
    """创建批量重命名脚本"""
    script_content = '''@echo off
chcp 65001 >nul
echo 开始修复文件名编码...
echo.

'''
    
    for file_info in problem_files:
        original = file_info['original']
        fixed = file_info.get('fixed')
        
        if fixed and fixed != original:
            script_content += f'''echo 重命名: "{original}"
echo   -> "{fixed}"
ren "{original}" "{fixed}"
if %errorlevel% equ 0 (
    echo   成功!
) else (
    echo   失败!
)
echo.
'''
    
    script_content += '''echo 修复完成!
pause
'''
    
    with open('fix_filenames.bat', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("批处理脚本已创建: fix_filenames.bat")
    print("双击运行此脚本执行重命名操作")

if __name__ == "__main__":
    print("分析Windows文件名编码问题")
    print("=" * 50)
    
    problem_files = analyze_windows_filenames()
    
    if problem_files:
        print(f"总共发现 {len(problem_files)} 个需要修复的文件")
        
        # 显示统计信息
        fixable = sum(1 for f in problem_files if f.get('fixed'))
        print(f"其中 {fixable} 个可以自动修复")
        
        if fixable > 0:
            create_batch_rename_script(problem_files)
        else:
            print("无法自动修复这些文件，需要手动处理")
    else:
        print("没有发现编码问题文件")