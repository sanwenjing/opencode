# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import re
from pathlib import Path

def check_mutagen():
    """检查mutagen库"""
    try:
        import mutagen
        return True
    except ImportError:
        print("安装 mutagen 中...")
        os.system(f"{sys.executable} -m pip install mutagen -q")
        try:
            import mutagen
            print("✓ 安装成功")
            return True
        except:
            print("✗ 安装失败")
            return False

def contains_replacement_char(text):
    """检测Unicode替换字符（真正的乱码）"""
    if not text or not isinstance(text, str):
        return False
    # Unicode替换字符 U+FFFD
    return '\ufffd' in text or '\uFFFD' in text

def contains_gbk_mojibake(text):
    """检测GBK乱码（UTF-8中文被误读为Latin1）"""
    if not text or not isinstance(text, str):
        return False
    
    # GBK乱码的典型模式：
    # UTF-8中文被错误地以Latin1解码，会产生 Ã Â Ä Æ È É Ê 等字符
    # 后跟 €-ÿ 范围内的字符（表示UTF-8多字节的后继字节）
    
    # 常见的GBK乱码起始字符
    gbk_prefixes = ['Ã', 'Â', 'Ä', 'Æ', 'È', 'É', 'Ê', 'Ë', 'Ì', 'Í', 'Î', 'Ï']
    
    # 检查是否包含这些前缀后跟高字节字符
    for prefix in gbk_prefixes:
        if prefix in text:
            # 检查后一个字符是否是非ASCII（>127）
            idx = text.find(prefix)
            if idx < len(text) - 1:
                next_char = text[idx + 1]
                if ord(next_char) > 127:
                    return True
    
    return False

def is_true_garbage(text):
    """判断是否为真正的乱码（不是误报）"""
    return contains_replacement_char(text) or contains_gbk_mojibake(text)

def try_decode_gbk_mojibake(text):
    """尝试修复GBK乱码"""
    # 将Latin1编码回字节，然后用GBK解码
    for encoding in ['gbk', 'gb2312', 'gb18030']:
        try:
            # 编码回Latin1字节
            bytes_data = text.encode('latin1')
            # 用GBK解码
            result = bytes_data.decode(encoding)
            # 验证结果：应该包含中文字符且无乱码
            if any('\u4e00' <= c <= '\u9fff' for c in result) and not is_true_garbage(result):
                return result
        except:
            continue
    return None

def try_decode_utf8_mojibake(text):
    """尝试修复UTF-8乱码"""
    try:
        bytes_data = text.encode('latin1')
        result = bytes_data.decode('utf-8')
        if not is_true_garbage(result):
            return result
    except:
        pass
    return None

def fix_garbage_text(text):
    """修复乱码文本"""
    if not is_true_garbage(text):
        return text
    
    print(f"    检测到乱码: {text[:50]}")
    
    # 策略1: 清理替换字符
    if contains_replacement_char(text):
        cleaned = text.replace('\ufffd', '').replace('\uFFFD', '')
        if cleaned and not is_true_garbage(cleaned):
            print(f"    ✓ 清理替换字符")
            return cleaned
    
    # 策略2: 修复GBK乱码
    if contains_gbk_mojibake(text):
        fixed = try_decode_gbk_mojibake(text)
        if fixed:
            print(f"    ✓ GBK修复: {fixed[:50]}")
            return fixed
    
    # 策略3: 修复UTF-8乱码
    fixed = try_decode_utf8_mojibake(text)
    if fixed:
        print(f"    ✓ UTF-8修复: {fixed[:50]}")
        return fixed
    
    # 策略4: Big5修复（繁体中文）
    try:
        bytes_data = text.encode('latin1')
        result = bytes_data.decode('big5')
        if not is_true_garbage(result):
            print(f"    ✓ Big5修复: {result[:50]}")
            return result
    except:
        pass
    
    print(f"    ⚠ 无法自动修复")
    return text

def scan_audio_files():
    """扫描音频文件标签"""
    print("\n" + "="*70)
    print("         🎵 音频文件ID3标签乱码扫描工具")
    print("="*70)
    
    if not check_mutagen():
        print("\n请安装: pip install mutagen")
        return
    
    import mutagen
    
    directory = Path('.')
    audio_extensions = {'.mp3', '.wma', '.wav', '.flac', '.m4a', '.ogg', '.aac'}
    audio_files = [f for f in directory.iterdir() if f.is_file() and f.suffix.lower() in audio_extensions]
    
    print(f"\n📁 找到 {len(audio_files)} 个音频文件\n")
    
    garbled_count = 0
    normal_count = 0
    error_count = 0
    no_tags_count = 0
    
    for idx, file_path in enumerate(audio_files, 1):
        print(f"[{idx:3d}/{len(audio_files)}] {file_path.name[:50]}")
        
        try:
            audio = mutagen.File(str(file_path))
            
            if audio is None:
                print("  ⚠ 无法识别文件格式")
                error_count += 1
                continue
            
            if not hasattr(audio, 'tags') or audio.tags is None:
                print("  ℹ 无ID3标签")
                no_tags_count += 1
                continue
            
            has_garbage = False
            fixed_items = []
            
            # 遍历所有标签
            for key, value in audio.tags.items():
                try:
                    text = None
                    
                    # 提取文本
                    if hasattr(value, 'text') and value.text:
                        text = str(value.text[0]) if value.text else None
                    elif isinstance(value, list) and value:
                        text = str(value[0])
                    elif isinstance(value, str):
                        text = value
                    
                    if text:
                        # 检测真正的乱码
                        if is_true_garbage(text):
                            has_garbage = True
                            fixed = fix_garbage_text(text)
                            if fixed != text:
                                fixed_items.append(f"{key}: {fixed[:40]}")
                            else:
                                fixed_items.append(f"{key}: [无法修复]")
                except:
                    pass
            
            if has_garbage:
                garbled_count += 1
                print(f"  ⚠ 发现 {len(fixed_items)} 个乱码标签")
                for item in fixed_items:
                    print(f"    → {item}")
            else:
                normal_count += 1
                print("  ✓ 标签正常")
        
        except Exception as e:
            print(f"  ✗ 处理错误: {e}")
            error_count += 1
        
        print()
    
    # 总结
    print("="*70)
    print("📊 扫描结果")
    print("="*70)
    print(f"  总计: {len(audio_files)}")
    print(f"  有乱码: {garbled_count}")
    print(f"  正常: {normal_count}")
    print(f"  无标签: {no_tags_count}")
    print(f"  错误: {error_count}")
    print("="*70)
    
    if garbled_count > 0:
        print(f"\n⚠ 发现 {garbled_count} 个文件有乱码标签")
        print("💡 建议使用 MP3Tag 或 foobar2000 手动修复")
    else:
        print("\n✅ 未发现乱码标签！")

def create_guide():
    """创建修复指南"""
    guide = '''# 音频文件ID3标签乱码修复指南

## 乱码识别

**真正的乱码：**
1. **替换字符**：显示为""（Unicode U+FFFD）
2. **GBK乱码**：如 "Ã¼Ã¶Ã¤Â§"（UTF-8中文被误存为Latin1）
   - 特征：包含 Ã Â Ä Æ 等字符

**不是乱码：**
- 正常中文："我爱你"
- 日文："あいうえお"  
- 韩文："안녕하세요"
- 特殊符号："♪ ♫ ★"

## 推荐修复工具

### MP3Tag（最简单 ⭐⭐⭐）

1. 下载：https://www.mp3tag.de/en/download.html
2. 拖拽音乐文件夹到窗口
3. 选中乱码文件 → 右键 → "转换" → "标签 - 文件名"
4. 选择编码：
   - GBK乱码 → 选择 **GBK**
   - UTF-8问题 → 选择 **UTF-8**
5. 保存

### foobar2000
1. 下载：https://www.foobar2000.org/download
2. 添加音乐 → 右键 → "属性"
3. 修改标签（可批量）

### MusicBee
1. 下载：https://getmusicbee.com/
2. 导入音乐库
3. 编辑标签

## 批量处理建议

1. **备份原文件**
2. **测试3-5个文件**
3. **确认无误后批量处理**

## 支持格式

MP3, WMA, FLAC, M4A, OGG, WAV, AAC

## 注意事项

⚠️ 修复前务必备份！
⚠️ 不确定时使用专业软件！
'''
    
    with open('音频标签修复指南.md', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("\n✓ 修复指南已创建: 音频标签修复指南.md")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("       🎵 音频文件ID3标签乱码扫描与修复")
    print("="*70)
    print("\n1. 扫描乱码标签")
    print("2. 创建修复指南")
    print("3. 退出")
    print("-"*70)
    
    try:
        choice = input("\n请选择 [1-3]: ").strip()
    except EOFError:
        choice = "1"
    
    if choice == "1":
        scan_audio_files()
    elif choice == "2":
        create_guide()
    else:
        print("\n已退出")
    
    print("\n" + "="*70)