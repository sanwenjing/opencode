#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilibili视频下载器
使用 bilibili-api-python 直接从B站API下载，无需浏览器
完全自动化，无需手动操作，自动合并音视频
"""

# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import re
import os
import json
import asyncio
import urllib.request
import argparse
import subprocess
import shutil
from typing import Optional
from bilibili_api import video


def extract_bvid(url: str) -> str:
    """从URL提取BV号"""
    if url.startswith('http'):
        match = re.search(r'BV[0-9a-zA-Z]{10,12}', url)
        if match:
            return match.group()
    else:
        return url
    return ''


def check_ffmpeg(auto_download: bool = True) -> Optional[str]:
    """检查系统是否安装ffmpeg，返回ffmpeg路径"""
    # 尝试在PATH中查找ffmpeg
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return ffmpeg_path
    
    # 尝试常见路径
    possible_paths = [
        'C:\\ffmpeg\\bin\\ffmpeg.exe',
        'C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe',
        'C:\\Program Files (x86)\\ffmpeg\\bin\\ffmpeg.exe',
        '/usr/bin/ffmpeg',
        '/usr/local/bin/ffmpeg',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # 尝试查找已下载的便携版
    local_ffmpeg = os.path.join(os.path.dirname(__file__), '..', 'ffmpeg', 'bin', 'ffmpeg.exe')
    if os.path.exists(local_ffmpeg):
        return local_ffmpeg
    
    # 自动下载ffmpeg（仅Windows）
    if auto_download and sys.platform == 'win32':
        return download_ffmpeg_portable()
    
    return None


def download_ffmpeg_portable() -> Optional[str]:
    """自动下载ffmpeg便携版（Windows）"""
    import zipfile
    import ssl
    
    try:
        print("\n[INFO] 正在自动下载ffmpeg便携版...")
        
        # 下载到技能目录
        skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ffmpeg_dir = os.path.join(skill_dir, 'ffmpeg')
        zip_path = os.path.join(ffmpeg_dir, 'ffmpeg.zip')
        
        # 创建目录
        os.makedirs(ffmpeg_dir, exist_ok=True)
        
        # 下载地址
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        
        # 禁用SSL验证
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        print(f"[INFO] 下载ffmpeg...")
        print(f"[INFO] 目标: {ffmpeg_dir}")
        
        # 下载
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        
        with urllib.request.urlopen(req, context=ssl_context, timeout=120) as response:
            with open(zip_path, 'wb') as f:
                f.write(response.read())
        
        print("[INFO] 解压中...")
        
        # 解压
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(ffmpeg_dir)
        
        # 查找ffmpeg.exe
        for root, dirs, files in os.walk(ffmpeg_dir):
            if 'ffmpeg.exe' in files:
                exe_path = os.path.join(root, 'ffmpeg.exe')
                
                # 移动到标准位置
                bin_dir = os.path.join(ffmpeg_dir, 'bin')
                os.makedirs(bin_dir, exist_ok=True)
                
                final_path = os.path.join(bin_dir, 'ffmpeg.exe')
                shutil.copy2(exe_path, final_path)
                
                # 清理
                try:
                    os.remove(zip_path)
                    # 删除临时解压目录
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d), ignore_errors=True)
                except:
                    pass
                
                print(f"[SUCCESS] ffmpeg下载成功: {final_path}")
                return final_path
        
        return None
        
    except Exception as e:
        print(f"[WARNING] 自动下载ffmpeg失败: {e}")
        return None


def install_ffmpeg_guide():
    """显示ffmpeg安装指南"""
    print("\n" + "=" * 70)
    print("[INFO] 未检测到ffmpeg，需要安装才能自动合并音视频")
    print("=" * 70)
    print("\nWindows安装方法:")
    print("1. 访问 https://ffmpeg.org/download.html")
    print("2. 下载Windows版本并解压到C:\\ffmpeg")
    print("3. 将C:\\ffmpeg\\bin添加到系统环境变量PATH")
    print("4. 重启命令行窗口")
    print("\n或使用包管理器安装:")
    print("  - Windows (choco): choco install ffmpeg")
    print("  - Windows (scoop): scoop install ffmpeg")
    print("  - Mac (brew): brew install ffmpeg")
    print("  - Linux (apt): sudo apt install ffmpeg")
    print("=" * 70)


def merge_video_audio(video_path: str, audio_path: str, output_path: str, ffmpeg_path: Optional[str] = None) -> bool:
    """
    使用ffmpeg合并音视频
    
    Args:
        video_path: 视频文件路径
        audio_path: 音频文件路径
        output_path: 输出文件路径
        ffmpeg_path: ffmpeg可执行文件路径（可选）
    
    Returns:
        合并是否成功
    """
    if not ffmpeg_path:
        ffmpeg_path = check_ffmpeg()
    
    if not ffmpeg_path:
        print("\n[ERROR] 未找到ffmpeg，无法自动合并")
        install_ffmpeg_guide()
        return False
    
    try:
        print(f"\n[INFO] 正在合并音视频...")
        print(f"[INFO] 使用ffmpeg: {ffmpeg_path}")
        
        # 构建ffmpeg命令
        cmd = [
            ffmpeg_path,
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            '-y',  # 覆盖输出文件
            output_path
        ]
        
        print(f"[INFO] 执行命令: {' '.join(cmd)}")
        
        # 执行命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            # 合并成功，删除原文件
            print("[INFO] 合并成功，清理临时文件...")
            try:
                os.remove(video_path)
                os.remove(audio_path)
                print(f"[INFO] 已删除: {os.path.basename(video_path)}")
                print(f"[INFO] 已删除: {os.path.basename(audio_path)}")
            except Exception as e:
                print(f"[WARNING] 清理临时文件失败: {e}")
            
            return True
        else:
            print(f"[ERROR] 合并失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] 合并过程出错: {e}")
        return False


async def download_video(bvid: str, output_dir: Optional[str] = None, auto_merge: bool = True):
    """
    下载视频的完整流程

    Args:
        bvid: BV号
        output_dir: 输出目录（如果为None则使用当前工作目录的downloads文件夹）
        auto_merge: 是否自动合并音视频（默认True）
    """
    # 确保output_dir是绝对路径，使用当前工作目录
    if output_dir is None:
        output_dir = os.path.abspath(os.path.join(os.getcwd(), 'downloads'))
    elif not os.path.isabs(output_dir):
        output_dir = os.path.abspath(output_dir)
    
    print("=" * 70)
    print("Bilibili视频下载器")
    print("=" * 70)
    print(f"BV号: {bvid}")
    print(f"输出目录: {output_dir}")
    print(f"自动合并: {'是' if auto_merge else '否'}")
    print("=" * 70)
    
    # 检查ffmpeg（如果需要自动合并）
    ffmpeg_path = None
    if auto_merge:
        ffmpeg_path = check_ffmpeg()
        if ffmpeg_path:
            print(f"[INFO] 检测到ffmpeg: {ffmpeg_path}")
        else:
            print("[WARNING] 未检测到ffmpeg，将只提供合并命令")
    
    # 1. 获取视频信息
    print("\n[INFO] 获取视频信息...")
    v = video.Video(bvid=bvid)
    info = await v.get_info()
    
    title = info.get('title', 'unknown')
    owner = info.get('owner', {}).get('name', 'unknown')
    duration = info.get('duration', 0)
    
    print(f"[INFO] 标题: {title}")
    print(f"[INFO] UP主: {owner}")
    print(f"[INFO] 时长: {duration}秒")
    
    # 2. 获取下载链接
    print("\n[INFO] 获取下载链接...")
    download_info = await v.get_download_url(page_index=0)
    
    urls = []
    
    # 解析DASH格式
    if 'dash' in download_info:
        dash = download_info['dash']
        
        # 视频流
        if 'video' in dash:
            for v_stream in dash['video']:
                urls.append({
                    'url': v_stream.get('baseUrl', v_stream.get('base_url', '')),
                    'quality': v_stream.get('id', 0),
                    'bandwidth': v_stream.get('bandwidth', 0),
                    'type': 'video'
                })
        
        # 音频流
        if 'audio' in dash:
            for a_stream in dash['audio']:
                urls.append({
                    'url': a_stream.get('baseUrl', a_stream.get('base_url', '')),
                    'quality': a_stream.get('id', 0),
                    'bandwidth': a_stream.get('bandwidth', 0),
                    'type': 'audio'
                })
    
    if not urls:
        print("[ERROR] 未找到下载链接")
        return False
    
    # 3. 分离音视频
    video_streams = [u for u in urls if u['type'] == 'video']
    audio_streams = [u for u in urls if u['type'] == 'audio']
    
    if not video_streams or not audio_streams:
        print("[ERROR] 未找到完整的音视频流")
        return False
    
    # 选择最佳质量
    best_video = max(video_streams, key=lambda x: x['bandwidth'])
    best_audio = max(audio_streams, key=lambda x: x['bandwidth'])
    
    print(f"[INFO] 视频画质: {best_video['quality']}P")
    print(f"[INFO] 音频质量: {best_audio['bandwidth']}bps")
    
    # 2. 为每个任务创建子文件夹
    os.makedirs(output_dir, exist_ok=True)
    safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)
    task_output_dir = os.path.join(output_dir, f"{bvid}_{safe_title}")
    os.makedirs(task_output_dir, exist_ok=True)

    print(f"[INFO] 任务文件夹: {task_output_dir}")

    # 下载视频（临时文件）
    video_filename = f"{safe_title}_video.mp4"
    video_path = os.path.join(task_output_dir, video_filename)

    print(f"\n[INFO] 下载视频: {video_filename}")
    if not download_file(best_video['url'], video_path):
        return False

    # 下载音频（临时文件）
    audio_filename = f"{safe_title}_audio.m4a"
    audio_path = os.path.join(task_output_dir, audio_filename)

    print(f"\n[INFO] 下载音频: {audio_filename}")
    if not download_file(best_audio['url'], audio_path):
        return False

    # 5. 合并音视频
    final_filename = f"{safe_title}.mp4"
    final_path = os.path.join(task_output_dir, final_filename)
    
    merge_success = False
    if auto_merge and ffmpeg_path:
        merge_success = merge_video_audio(video_path, audio_path, final_path, ffmpeg_path)
    
    # 6. 完成
    print("\n" + "=" * 70)
    if merge_success:
        print("✓ 下载并合并完成！")
        print("=" * 70)
        print(f"最终文件: {final_filename}")
        print(f"文件路径: {final_path}")
        print(f"文件大小: {os.path.getsize(final_path) / 1024 / 1024:.2f} MB")
    else:
        print("✓ 下载完成！（未合并）")
        print("=" * 70)
        print(f"视频文件: {video_filename}")
        print(f"音频文件: {audio_filename}")
        if auto_merge and not ffmpeg_path:
            print("\n提示: 未检测到ffmpeg，音视频未自动合并")
            print("请手动安装ffmpeg后运行以下命令合并:")
            print(f'  ffmpeg -i "{video_filename}" -i "{audio_filename}" -c:v copy -c:a aac "{final_filename}"')
    print("=" * 70)
    
    return True


def download_file(url: str, file_path: str) -> bool:
    """下载单个文件"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.bilibili.com',
        }
        
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=300) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"  进度: {progress:.1f}%", end='\r')
            
            file_size = os.path.getsize(file_path)
            print(f"\n  ✓ 完成! 大小: {file_size / 1024 / 1024:.2f} MB")
            return True
            
    except Exception as e:
        print(f"\n  ✗ 下载失败: {e}")
        return False


async def main():
    parser = argparse.ArgumentParser(
        description='Bilibili视频下载器 - 全自动版（支持自动合并）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python scripts/download.py "https://www.bilibili.com/video/BV1mZrKBAEHf/"
  python scripts/download.py "BV1mZrKBAEHf" -o ./downloads
  python scripts/download.py "BV1mZrKBAEHf" --no-merge  # 不自动合并

说明:
  本脚本使用bilibili-api库直接从B站API下载视频
  自动下载音视频并使用ffmpeg合并
  如果未安装ffmpeg，将提供合并命令
        """
    )
    
    parser.add_argument('url', help='Bilibili视频链接或BV号')
    parser.add_argument('-o', '--output', default=None, help='下载输出目录 (默认: 当前工作目录下的downloads文件夹)')
    parser.add_argument('--no-merge', action='store_true', help='禁用自动合并音视频')
    
    args = parser.parse_args()

    # 使用当前工作目录的绝对路径作为默认下载目录
    default_output = os.path.abspath(os.path.join(os.getcwd(), 'downloads'))

    # 提取BV号
    bvid = extract_bvid(args.url)
    if not bvid:
        print("[ERROR] 无法提取BV号")
        sys.exit(1)

    # 确定输出目录（优先使用用户指定，否则使用当前工作目录的downloads文件夹）
    if args.output and args.output != './downloads':
        output_dir = os.path.abspath(args.output)
    else:
        output_dir = default_output

    # 下载（自动合并，除非指定--no-merge）
    auto_merge = not args.no_merge
    success = await download_video(bvid, output_dir, auto_merge)
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
