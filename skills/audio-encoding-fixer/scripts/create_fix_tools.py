# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
from pathlib import Path

def create_simple_bat_fix():
    """创建简单的批处理修复脚本"""
    print("创建简单修复脚本...")
    
    # 首先获取当前目录中的音频文件列表
    directory = Path('.')
    audio_extensions = {'.mp3', '.wma', '.wav', '.flac', '.m4a', '.ogg'}
    
    files_to_check = []
    for item in directory.iterdir():
        if item.is_file() and item.suffix.lower() in audio_extensions:
            files_to_check.append(item.name)
    
    # 创建批处理脚本
    bat_content = '''@echo off
chcp 65001 >nul
echo 音频文件名编码修复工具
echo ========================
echo.
echo 检查文件名编码问题...
echo.
'''
    
    # 添加文件检查
    for filename in files_to_check:
        bat_content += f'echo 检查: {filename}\n'
    
    bat_content += '''
echo.
echo 请手动检查上述文件名是否包含乱码字符。
echo 如果发现乱码，请使用以下命令格式手动修复：
echo ren "乱码文件名.mp3" "正确文件名.mp3"
echo.
echo 或者运行Python脚本进行自动修复...
echo.
pause
'''
    
    with open('check_filenames.bat', 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    print("检查脚本已创建: check_filenames.bat")
    print("双击运行此脚本查看文件名情况")

def create_python_id3_fix():
    """创建ID3标签修复脚本"""
    script_content = '''# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
from pathlib import Path

def install_mutagen():
    """安装mutagen库"""
    try:
        import mutagen
        return True
    except ImportError:
        print("正在安装mutagen库...")
        os.system(f"{sys.executable} -m pip install mutagen")
        try:
            import mutagen
            return True
        except:
            return False

def fix_audio_tags():
    """修复音频文件ID3标签"""
    if not install_mutagen():
        print("无法安装mutagen库，跳过标签修复")
        return
    
    from mutagen.id3 import ID3, TIT2, TPE1, TALB
    from mutagen.mp3 import MP3
    from mutagen.wma import WMA
    
    print("开始修复音频文件标签...")
    print("=" * 50)
    
    directory = Path('.')
    audio_extensions = {'.mp3', '.wma', '.wav', '.flac', '.m4a', '.ogg'}
    fixed_count = 0
    
    for item in directory.iterdir():
        if item.is_file() and item.suffix.lower() in audio_extensions:
            try:
                print(f"\\n处理文件: {item.name}")
                
                if item.suffix.lower() == '.mp3':
                    # 处理MP3文件
                    try:
                        audio = MP3(str(item))
                        if audio.tags is None:
                            audio.add_tags()
                        
                        # 尝试修复标题
                        if 'TIT2' in audio:
                            title = audio['TIT2'].text[0] if audio['TIT2'].text else ''
                            if title and '�' in title:
                                print(f"  发现乱码标题: {title}")
                                # 尝试编码转换
                                fixed_title = fix_text_encoding(title)
                                if fixed_title != title:
                                    audio.tags.add(TIT2(encoding=3, text=fixed_title))
                                    print(f"  修复标题: {fixed_title}")
                                    audio.save()
                                    fixed_count += 1
                        
                        # 尝试修复艺术家
                        if 'TPE1' in audio:
                            artist = audio['TPE1'].text[0] if audio['TPE1'].text else ''
                            if artist and '�' in artist:
                                print(f"  发现乱码艺术家: {artist}")
                                fixed_artist = fix_text_encoding(artist)
                                if fixed_artist != artist:
                                    audio.tags.add(TPE1(encoding=3, text=fixed_artist))
                                    print(f"  修复艺术家: {fixed_artist}")
                                    audio.save()
                                    fixed_count += 1
                    
                    except Exception as e:
                        print(f"  MP3处理失败: {e}")
                
                elif item.suffix.lower() == '.wma':
                    # 处理WMA文件
                    try:
                        audio = WMA(str(item))
                        # 检查和修复WMA标签...
                        print(f"  WMA文件标签检查")
                    except Exception as e:
                        print(f"  WMA处理失败: {e}")
                
            except Exception as e:
                print(f"  文件处理失败: {e}")
    
    print(f"\\n标签修复完成! 修复了 {fixed_count} 个标签")

def fix_text_encoding(text):
    """修复文本编码"""
    if not text or '�' not in text:
        return text
    
    # 尝试多种编码转换
    try:
        # 方法1: 从latin1字节转换
        latin1_bytes = text.encode('latin1', errors='ignore')
        for encoding in ['gbk', 'gb2312', 'gb18030', 'cp936', 'big5']:
            try:
                fixed = latin1_bytes.decode(encoding)
                if any('\\u4e00' <= c <= '\\u9fff' for c in fixed) and '�' not in fixed:
                    return fixed
            except:
                continue
    except:
        pass
    
    return text

if __name__ == "__main__":
    fix_audio_tags()
'''
    
    with open('fix_audio_tags.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("ID3标签修复脚本已创建: fix_audio_tags.py")

def create_comprehensive_solution():
    """创建综合解决方案"""
    print("创建综合解决方案...")
    
    solution_script = '''# 设置控制台编码为UTF-8
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
        print("\\n" + "="*50)
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
    print("\\n检查文件名编码问题...")
    print("-"*40)
    
    directory = Path('.')
    audio_extensions = {'.mp3', '.wma', '.wav', '.flac', '.m4a', '.ogg'}
    
    for item in directory.iterdir():
        if item.is_file() and item.suffix.lower() in audio_extensions:
            filename = item.name
            if '�' in filename:
                print(f"发现乱码: {filename}")
    
    print("\\n检查完成")

def manual_fix_helper():
    """手动修复助手"""
    print("\\n手动修复助手")
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
                if any('\\u4e00' <= c <= '\\u9fff' for c in fixed) and '�' not in fixed:
                    return fixed
            except:
                continue
    except:
        pass
    
    return filename

def batch_rename_tool():
    """批量重命名工具"""
    print("\\n批量重命名工具")
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
'''
    
    with open('audio_encoding_fix_tool.py', 'w', encoding='utf-8') as f:
        f.write(solution_script)
    
    print("综合工具已创建: audio_encoding_fix_tool.py")

if __name__ == "__main__":
    print("音频编码修复解决方案")
    print("=" * 50)
    print("正在创建工具...")
    
    create_simple_bat_fix()
    create_python_id3_fix()
    create_comprehensive_solution()
    
    print("\\n所有工具已创建完成!")
    print("\\n可用的修复工具:")
    print("1. check_filenames.bat - 检查文件名情况")
    print("2. fix_audio_tags.py - 修复音频ID3标签")
    print("3. audio_encoding_fix_tool.py - 综合修复工具")
    print("\\n推荐使用: python audio_encoding_fix_tool.py")