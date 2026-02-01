# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import re
from pathlib import Path

def install_mutagen():
    """检查并安装mutagen库"""
    try:
        import mutagen
        return True
    except ImportError:
        print("正在安装 mutagen 库...")
        os.system(f"{sys.executable} -m pip install mutagen -q")
        try:
            import mutagen
            print("✓ mutagen 安装成功")
            return True
        except ImportError:
            print("✗ mutagen 安装失败")
            return False

def parse_filename(filename):
    """从文件名解析歌曲名和歌手"""
    # 移除扩展名
    name_without_ext = Path(filename).stem
    
    # 模式1: " - " (最常见)
    if " - " in name_without_ext:
        parts = name_without_ext.split(" - ", 1)
        if len(parts) == 2:
            title = parts[0].strip()
            artist = parts[1].strip()
            return title, artist
    
    # 模式2: "-" (无空格)
    if "-" in name_without_ext and " - " not in name_without_ext:
        parts = name_without_ext.split("-", 1)
        if len(parts) == 2:
            title = parts[0].strip()
            artist = parts[1].strip()
            return title, artist
    
    # 模式3: 纯歌曲名（无歌手）
    return name_without_ext.strip(), ""

def write_tags_to_file(file_path, title, artist, album):
    """将标签写入音乐文件"""
    try:
        import mutagen
        from mutagen.id3 import TIT2, TPE1, TALB
        
        audio = mutagen.File(str(file_path))
        
        if audio is None:
            return False, "无法识别文件格式"
        
        # 确保有标签
        if audio.tags is None:
            try:
                audio.add_tags()
            except:
                return False, "无法添加标签"
        
        file_ext = file_path.suffix.lower()
        has_changes = False
        changes_info = []
        
        if file_ext == '.mp3':
            # MP3使用ID3标签
            if title:
                try:
                    audio.tags["TIT2"] = TIT2(encoding=1, text=title)
                    has_changes = True
                    changes_info.append(f"标题: {title[:30]}")
                except:
                    pass
            
            if artist:
                try:
                    audio.tags["TPE1"] = TPE1(encoding=1, text=artist)
                    has_changes = True
                    changes_info.append(f"艺术家: {artist[:30]}")
                except:
                    pass
            
            if album:
                try:
                    audio.tags["TALB"] = TALB(encoding=1, text=album)
                    has_changes = True
                    changes_info.append(f"唱片集: {album[:30]}")
                except:
                    pass
        
        elif file_ext == '.wma':
            # WMA使用ASF标签
            if title:
                try:
                    audio.tags['Title'] = title
                    has_changes = True
                    changes_info.append(f"标题: {title[:30]}")
                except:
                    pass
            
            if artist:
                try:
                    audio.tags['Author'] = artist
                    has_changes = True
                    changes_info.append(f"艺术家: {artist[:30]}")
                except:
                    pass
            
            if album:
                try:
                    audio.tags['WM/AlbumTitle'] = album
                    has_changes = True
                    changes_info.append(f"唱片集: {album[:30]}")
                except:
                    pass
        
        else:
            # 其他格式尝试通用方法
            if title:
                try:
                    audio.tags['title'] = title
                    has_changes = True
                    changes_info.append(f"标题: {title[:30]}")
                except:
                    pass
            
            if artist:
                try:
                    audio.tags['artist'] = artist
                    has_changes = True
                    changes_info.append(f"艺术家: {artist[:30]}")
                except:
                    pass
            
            if album:
                try:
                    audio.tags['album'] = album
                    has_changes = True
                    changes_info.append(f"唱片集: {album[:30]}")
                except:
                    pass
        
        if has_changes:
            try:
                audio.save()
                return True, "; ".join(changes_info)
            except Exception as e:
                return False, f"保存失败: {e}"
        
        return False, "无需修改"
    
    except Exception as e:
        return False, f"处理错误: {e}"

def auto_tag_from_filename():
    """从文件名自动提取并写入所有标签"""
    print("\n" + "="*70)
    print("         🎵 从文件名自动提取并写入标签")
    print("="*70)
    print("\n✅ 功能说明:")
    print("  • 解析文件名提取歌曲名和歌手")
    print("  • 写入标题(TIT2)和艺术家(TPE1)字段")
    print("  • 完整文件名写入唱片集(TALB)字段")
    print("  • 使用UTF-8编码\n")
    
    if not install_mutagen():
        print("错误：无法安装 mutagen 库")
        print("请手动运行: pip install mutagen")
        return
    
    directory = Path('.')
    audio_extensions = {'.mp3', '.wma', '.wav', '.flac', '.m4a', '.ogg', '.aac'}
    
    audio_files = [f for f in directory.iterdir() 
                   if f.is_file() and f.suffix.lower() in audio_extensions]
    
    if not audio_files:
        print("❌ 未找到音频文件")
        return
    
    print(f"📁 找到 {len(audio_files)} 个音频文件\n")
    
    # 显示前3个文件名示例
    print("文件名示例:")
    for i, f in enumerate(audio_files[:3], 1):
        title, artist = parse_filename(f.name)
        print(f"  {i}. {f.name}")
        print(f"     → 标题: {title}, 艺术家: {artist}")
    print()
    
    # 确认是否继续
    try:
        confirm = input("是否开始写入标签? (y/n): ").strip().lower()
    except EOFError:
        confirm = "y"
    
    if confirm != "y":
        print("\n已取消")
        return
    
    print("\n开始处理...\n")
    
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    for idx, file_path in enumerate(audio_files, 1):
        # 解析文件名
        title, artist = parse_filename(file_path.name)
        album = file_path.stem  # 完整文件名作为唱片集
        
        print(f"[{idx:3d}/{len(audio_files)}] {file_path.name[:50]}")
        
        # 写入标签
        success, message = write_tags_to_file(file_path, title, artist, album)
        
        if success:
            print(f"      ✓ {message}")
            success_count += 1
        elif "无需修改" in message:
            print(f"      ⚠ {message}")
            skipped_count += 1
        else:
            print(f"      ✗ {message}")
            failed_count += 1
        
        print()
    
    # 输出总结
    print("="*70)
    print("📊 处理结果")
    print("="*70)
    print(f"  总计:     {len(audio_files)}")
    print(f"  成功:     {success_count}")
    print(f"  跳过:     {skipped_count}")
    print(f"  失败:     {failed_count}")
    print("="*70)
    
    if success_count > 0:
        print(f"\n✅ 成功为 {success_count} 个文件写入标签！")
        print("\n💡 现在您可以在音乐播放器中查看完整的标签信息了。")
    
    if failed_count > 0:
        print(f"\n⚠️  {failed_count} 个文件处理失败")

if __name__ == "__main__":
    auto_tag_from_filename()
    print("\n" + "="*70)