# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
from pathlib import Path

def main_menu():
    """主菜单"""
    while True:
        print("\n" + "="*50)
        print("    音频文件编码修复工具")
        print("="*50)
        print("1. 检查文件名编码问题")
        print("2. 修复音频文件ID3标签")
        print("3. 手动文件名编码修复助手")
        print("4. 批量重命名工具")
        print("5. 退出")
        print("-"*50)
        
        choice = input("请选择操作 (1-5): ").strip()
        
        if choice == '1':
            check_filename_encoding()
        elif choice == '2':
            os.system(f"{sys.executable} fix_audio_tags.py")
        elif choice == '3':
            manual_fix_helper()
        elif choice == '4':
            batch_rename_tool()
        elif choice == '5':
            print("退出程序")
            break
        else:
            print("无效选择，请重试")

def check_filename_encoding():
    """检查文件名编码"""
    print("\n检查文件名编码问题...")
    print("-"*40)
    
    directory = Path('.')
    audio_extensions = {'.mp3', '.wma', '.wav', '.flac', '.m4a', '.ogg'}
    
    for item in directory.iterdir():
        if item.is_file() and item.suffix.lower() in audio_extensions:
            filename = item.name
            if '�' in filename:
                print(f"发现乱码: {filename}")
    
    print("\n检查完成")

def manual_fix_helper():
    """手动修复助手"""
    print("\n手动修复助手")
    print("请提供要修复的文件名:")
    
    filename = input("文件名: ").strip()
    if not filename or not os.path.exists(filename):
        print("文件不存在")
        return
    
    print(f"原文件名: {filename}")
    
    # 尝试自动修复
    fixed = try_auto_fix(filename)
    if fixed != filename:
        print(f"建议修复为: {fixed}")
        use_fix = input("使用此修复结果吗? (y/n): ").strip().lower()
        if use_fix == 'y':
            try:
                os.rename(filename, fixed)
                print("重命名成功!")
            except Exception as e:
                print(f"重命名失败: {e}")
    else:
        print("无法自动修复，请手动提供正确名称")
        manual_name = input("正确文件名: ").strip()
        if manual_name:
            try:
                os.rename(filename, manual_name)
                print("重命名成功!")
            except Exception as e:
                print(f"重命名失败: {e}")

def try_auto_fix(filename):
    """尝试自动修复文件名"""
    if '�' not in filename:
        return filename
    
    try:
        latin1_bytes = filename.encode('latin1', errors='ignore')
        for encoding in ['gbk', 'gb2312', 'gb18030', 'cp936']:
            try:
                fixed = latin1_bytes.decode(encoding)
                if any('\u4e00' <= c <= '\u9fff' for c in fixed) and '�' not in fixed:
                    return fixed
            except:
                continue
    except:
        pass
    
    return filename

def batch_rename_tool():
    """批量重命名工具"""
    print("\n批量重命名工具")
    print("此功能将创建一个批处理文件供您编辑和执行")
    
    directory = Path('.')
    audio_extensions = {'.mp3', '.wma', '.wav', '.flac', '.m4a', '.ogg'}
    
    batch_content = '@echo off\n'
    batch_content += 'chcp 65001 >nul\n'
    batch_content += 'echo 批量重命名脚本\n'
    batch_content += 'echo.\n'
    
    for item in directory.iterdir():
        if item.is_file() and item.suffix.lower() in audio_extensions:
            filename = item.name
            if '�' in filename:
                fixed = try_auto_fix(filename)
                batch_content += f'echo 原文件名: "{filename}"\n'
                batch_content += f'echo 建议名称: "{fixed}"\n'
                batch_content += 'echo.\n'
                batch_content += f'rem ren "{filename}" "{fixed}"\n'
    
    batch_content += 'echo 批量重命名完成\n'
    batch_content += 'pause\n'
    
    with open('batch_rename.bat', 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    print("批处理文件已创建: batch_rename.bat")
    print("请编辑此文件，取消注释需要的重命名命令，然后运行")

if __name__ == "__main__":
    main_menu()