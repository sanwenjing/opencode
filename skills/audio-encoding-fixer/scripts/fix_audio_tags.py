# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import re
from pathlib import Path

def install_and_check_mutagen():
    """检查并安装mutagen库"""
    try:
        import mutagen
        return True
    except ImportError:
        print("正在安装mutagen库...")
        os.system(f"{sys.executable} -m pip install mutagen -q")
        try:
            import mutagen
            print("✓ mutagen安装成功")
            return True
        except ImportError:
            print("✗ mutagen安装失败")
            return False

def is_garbled_text(text):
    """检测真正的乱码文本"""
    if not text or not isinstance(text, str):
        return False
    
    # 真正的乱码特征1: Unicode替换字符
    if '\ufffd' in text:
        return True
    
    # 真正的乱码特征2: GBK/UTF-8被误读为Latin1
    # 典型模式：Ã, Â, Ä 后跟字节值大于127的字符
    garbled_pattern = r'[ÃÂÄÆÈÉÊ-][-ÿ]'
    if re.search(garbled_pattern, text):
        return True
    
    return False

def try_fix_encoding(text):
    """尝试修复乱码文本"""
    if not is_garbled_text(text):
        return text
    
    original_text = text
    
    # 策略1: 如果包含替换字符，尝试清理
    if '\ufffd' in text:
        # 可能是UTF-8字节流被截断
        try:
            # 尝试直接UTF-8解码（某些情况下有效）
            result = text.encode('utf-8', errors='ignore').decode('utf-8')
            if result and not is_garbled_text(result):
                return result
        except:
            pass
    
    # 策略2: GBK乱码修复（UTF-8中文被误存为Latin1）
    # 典型情况：中文被显示为 Ã¶Ã¤Â§ 等
    if re.search(r'[ÃÂÄ]', text):
        for encoding in ['gbk', 'gb2312', 'gb18030']:
            try:
                # 先将Latin1编码回字节，再用正确编码解码
                bytes_data = text.encode('latin1')
                result = bytes_data.decode(encoding)
                if not is_garbled_text(result) and any('\u4e00' <= c <= '\u9fff' for c in result):
                    return result
            except:
                continue
    
    # 策略3: UTF-8修复
    try:
        bytes_data = text.encode('latin1')
        result = bytes_data.decode('utf-8')
        if not is_garbled_text(result):
            return result
    except:
        pass
    
    # 策略4: Big5修复（繁体中文）
    try:
        bytes_data = text.encode('latin1')
        result = bytes_data.decode('big5')
        if not is_garbled_text(result):
            return result
    except:
        pass
    
    return original_text

def scan_and_report():
    """扫描并报告乱码情况"""
    print("\n" + "="*70)
    print("         音频文件ID3标签扫描报告")
    print("="*70)
    
    if not install_and_check_mutagen():
        print("请先手动安装: pip install mutagen")
        return
    
    import mutagen
    
    directory = Path('.')
    audio_extensions = {'.mp3', '.wma', '.wav', '.flac', '.m4a', '.ogg', '.aac'}
    
    files = [f for f in directory.iterdir() if f.is_file() and f.suffix.lower() in audio_extensions]
    
    print(f"\n📁 找到 {len(files)} 个音频文件\n")
    
    garbled_files = []
    
    for idx, file_path in enumerate(files, 1):
        print(f"[{idx:3d}/{len(files)}] {file_path.name[:50]}")
        
        try:
            audio = mutagen.File(str(file_path))
            
            if audio is None:
                print("  ⚠ 无法识别格式")
                continue
            
            if not hasattr(audio, 'tags') or audio.tags is None:
                print("  ℹ 无标签")
                continue
            
            file_has_garbage = False
            problems = []
            
            for key, value in audio.tags.items():
                try:
                    text = None
                    
                    # 提取文本值
                    if hasattr(value, 'text') and value.text:
                        text = str(value.text[0])
                    elif isinstance(value, list) and value:
                        text = str(value[0])
                    elif isinstance(value, str):
                        text = value
                    
                    if text and is_garbled_text(text):
                        file_has_garbage = True
                        fixed = try_fix_encoding(text)
                        problems.append({
                            'key': key,
                            'original': text,
                            'fixed': fixed if fixed != text else None
                        })
                except:
                    pass
            
            if file_has_garbage:
                garbled_files.append({
                    'file': file_path.name,
                    'problems': problems
                })
                print(f"  ⚠ 发现 {len(problems)} 个乱码标签")
                for p in problems:
                    if p['fixed']:
                        print(f"    {p['key']}: {p['original'][:30]} → {p['fixed'][:30]}")
                    else:
                        print(f"    {p['key']}: {p['original'][:30]} (无法自动修复)")
            else:
                print("  ✓ 正常")
        
        except Exception as e:
            print(f"  ✗ 错误: {e}")
        
        print()
    
    # 输出总结
    print("="*70)
    print("📊 扫描结果")
    print("="*70)
    print(f"总文件数: {len(files)}")
    print(f"有乱码文件: {len(garbled_files)}")
    print(f"正常文件: {len(files) - len(garbled_files)}")
    print("="*70)
    
    if garbled_files:
        print("\n⚠ 发现乱码的文件列表:")
        for gf in garbled_files:
            print(f"  - {gf['file']}")
        print("\n💡 建议使用 MP3Tag 或 foobar2000 手动修复")
    else:
        print("\n✅ 未发现乱码标签！")

def create_guide():
    """创建修复指南"""
    guide = '''# 音频文件ID3标签乱码修复指南

## 乱码识别

**真正的乱码示例：**
- 包含问号：""（Unicode替换字符 U+FFFD）
- GBK乱码："Ã¼Ã¶Ã¤Â§"（UTF-8中文被误读为Latin1）
- 混合乱码："Ã¼â€œâ€Ââ€â€

**不是乱码：**
- 正常中文："我爱你"
- 日文："あいうえお"
- 韩文："안녕하세요"
- 特殊符号："♪ ♫ ★"

## 修复方法

### 推荐：使用 MP3Tag（免费且最简单）

1. 下载：https://www.mp3tag.de/en/download.html
2. 拖拽音乐文件夹到 MP3Tag 窗口
3. 选中乱码文件 → 右键 → "转换" → "标签 - 文件名"
4. 选择编码：
   - 如果是 GBK 乱码 → 选择 **GBK** 或 **GB2312**
   - 如果是 UTF-8 问题 → 选择 **UTF-8**
5. 点击确定保存

### 备选：foobar2000

1. 下载：https://www.foobar2000.org/download
2. 添加音乐文件 → 右键 → "属性"
3. 修改元数据标签
4. 支持批量修改

### 备选：MusicBee

1. 下载：https://getmusicbee.com/
2. 导入音乐库
3. 编辑标签并保存

## 批量处理建议

1. **先备份**：复制音乐文件夹
2. **测试**：先修复3-5个文件验证
3. **批量**：确认无误后处理全部

## 支持的格式

MP3, WMA, FLAC, M4A, OGG, WAV, AAC

## 注意事项

⚠️ 务必先备份！
⚠️ 批量操作前先测试！
⚠️ 无法确定时使用专业软件手动修复！
'''
    
    with open('音频标签修复指南.md', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("\n✓ 修复指南已创建: 音频标签修复指南.md")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("       🎵 音频文件ID3标签乱码修复工具")
    print("="*70)
    print("\n1. 扫描乱码标签")
    print("2. 创建修复指南")
    print("3. 退出")
    print("-"*70)
    
    try:
        choice = input("\n选择 [1-3]: ").strip()
    except EOFError:
        choice = "1"
    
    if choice == "1":
        scan_and_report()
    elif choice == "2":
        create_guide()
    else:
        print("\n已退出")
    
    print("\n" + "="*70)