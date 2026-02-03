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
import configparser
from typing import Optional, List, Dict
from bilibili_api import video, Credential


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


def load_credential():
    """
    加载B站登录凭证（支持cookies配置）
    
    配置文件格式 (config.ini):
    [bilibili]
    # 方式1: 完整的Cookie字符串（推荐，从浏览器复制）
    cookie = 完整的cookie字符串
    
    # 方式2: 分别填入各字段
    sessdata = 你的SESSDATA值
    buvid3 = 你的BUVID3值
    bili_jct = 你的BILI_JCT值
    
    获取方法：
    1. 登录B站网页版 (https://www.bilibili.com)
    2. 按F12打开开发者工具
    3. 切换到Network(网络)标签
    4. 刷新页面，点击任意请求（如www.bilibili.com）
    5. 在Request Headers中找到Cookie字段
    6. 复制整个Cookie值
    """
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
    
    if not os.path.exists(config_path):
        print("[INFO] 未找到配置文件config.ini，将使用未登录状态下载（画质受限）")
        print("[INFO] 如需下载高清画质，请创建配置文件config.ini")
        print("[INFO] 配置文件路径:", os.path.normpath(config_path))
        return None
    
    try:
        # 直接读取文件，手动解析
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 手动解析ini文件
        cookie = ''
        sessdata = ''
        buvid3 = ''
        bili_jct = ''
        
        in_bilibili_section = False
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('[') and line.endswith(']'):
                in_bilibili_section = (line == '[bilibili]')
                continue
            if in_bilibili_section and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip().lower()
                value = value.strip()
                if key == 'cookie':
                    cookie = value
                elif key == 'sessdata':
                    sessdata = value
                elif key == 'buvid3':
                    buvid3 = value
                elif key == 'bili_jct':
                    bili_jct = value
        
        if cookie:
            # 从完整cookie字符串中提取各字段
            for item in cookie.split(';'):
                item = item.strip()
                if item.startswith('SESSDATA='):
                    sessdata = item.split('=')[1]
                elif item.startswith('buvid3='):
                    buvid3 = item.split('=')[1]
                elif item.startswith('bili_jct='):
                    bili_jct = item.split('=')[1]
            
            if not sessdata or not buvid3 or not bili_jct:
                print("[WARNING] Cookie格式不完整，需要包含SESSDATA, buvid3, bili_jct")
                return None
            
            cred = Credential(sessdata=sessdata, buvid3=buvid3, bili_jct=bili_jct)
            return cred
        
        if not sessdata or not buvid3 or not bili_jct:
            print("[WARNING] 配置项不完整，需要sessdata, buvid3, bili_jct")
            return None
        
        cred = Credential(sessdata=sessdata, buvid3=buvid3, bili_jct=bili_jct)
        return cred
        
    except Exception as e:
        print(f"[WARNING] 加载配置文件失败: {e}")
        return None


async def verify_credential(credential: Credential) -> tuple:
    """
    验证凭证是否有效
    
    Returns:
        (is_valid, vip_status, level)
    """
    try:
        # 尝试访问需要登录的API来验证凭证
        from bilibili_api import video
        v = video.Video(bvid='BV1ux411c7h8', credential=credential)
        info = await v.get_info()
        
        if info and info.get('owner'):
            # 凭证有效
            return True, False, 0
        
        return False, False, 0
        
    except Exception as e:
        error_str = str(e).lower()
        if 'auth' in error_str or 'login' in error_str or 'credential' in error_str or '403' in error_str:
            return False, False, 0
        # 其他错误可能只是视频不存在，但凭证可能有效
        return True, False, 0
    
    try:
        config = configparser.ConfigParser()
        config.read(config_path, encoding='utf-8')
        
        if 'bilibili' not in config:
            print("[WARNING] 配置文件中缺少[bilibili] section")
            return None
        
        # 优先使用完整cookie字段
        cookie = config.get('bilibili', 'cookie', fallback='').strip()
        
        if cookie:
            # 从完整cookie字符串中提取各字段
            sessdata = ''
            buvid3 = ''
            bili_jct = ''
            
            for item in cookie.split(';'):
                item = item.strip()
                if item.startswith('SESSDATA='):
                    sessdata = item.split('=')[1]
                elif item.startswith('buvid3='):
                    buvid3 = item.split('=')[1]
                elif item.startswith('bili_jct='):
                    bili_jct = item.split('=')[1]
            
            if not sessdata or not buvid3 or not bili_jct:
                print("[WARNING] Cookie格式不完整，需要包含SESSDATA, buvid3, bili_jct")
                return None
            
            print("[INFO] 已从完整Cookie加载登录凭证")
            cred = Credential(sessdata=sessdata, buvid3=buvid3, bili_jct=bili_jct)
            print("[INFO] 将尝试下载高清画质")
            return cred
        
        # 兼容旧方式：分别填写各字段
        sessdata = config.get('bilibili', 'sessdata', fallback='').strip()
        buvid3 = config.get('bilibili', 'buvid3', fallback='').strip()
        bili_jct = config.get('bilibili', 'bili_jct', fallback='').strip()
        
        if not sessdata or not buvid3 or not bili_jct:
            print("[WARNING] 配置项不完整，需要sessdata, buvid3, bili_jct")
            return None
        
        cred = Credential(sessdata=sessdata, buvid3=buvid3, bili_jct=bili_jct)
        print("[INFO] 已加载登录凭证，将尝试下载高清画质")
        return cred
        
    except Exception as e:
        print(f"[WARNING] 加载配置文件失败: {e}")
        return None


def get_video_codecs(download_info: dict) -> List[Dict]:
    """获取可用的视频编码列表"""
    codecs = []
    if 'dash' in download_info and 'video' in download_info['dash']:
        for v in download_info['dash']['video']:
            codecs.append({
                'id': v.get('id'),
                'codecs': v.get('codecs', ''),
                'bandwidth': v.get('bandwidth', 0),
                'baseUrl': v.get('baseUrl', v.get('base_url', ''))
            })
    return codecs


def get_quality_name(quality_id: int) -> str:
    """将画质ID转换为可读名称"""
    quality_map = {
        6: '240P',
        16: '360P',
        32: '480P',
        48: '720P',
        64: '720P+',
        74: '1080P',
        80: '1080P+',
        112: '4K',
    }
    return quality_map.get(quality_id, f'{quality_id}P')


def select_best_video_stream(urls: list) -> Optional[Dict]:
    """
    选择最佳视频流
    优先级：
    1. 按画质id选择最高（id越大画质越好：16=360P, 32=480P, 64=720P, 80=1080P）
    2. 同画质下优先H.264编码（兼容性最好）
    3. 排除AV1等可能不兼容的编码
    """
    video_streams = [u for u in urls if u['type'] == 'video']
    
    if not video_streams:
        return None
    
    # 按画质id分组
    quality_groups = {}
    for v in video_streams:
        qid = v.get('quality', 0)
        if qid not in quality_groups:
            quality_groups[qid] = []
        quality_groups[qid].append(v)
    
    # 选择最高画质
    if not quality_groups:
        return None
    
    highest_quality = max(quality_groups.keys())
    highest_streams = quality_groups[highest_quality]
    
    # 在最高画质中优先选择H.264编码
    h264_streams = [v for v in highest_streams if 'avc' in v.get('codecs', '').lower()]
    
    if h264_streams:
        # 返回带宽最高的
        return max(h264_streams, key=lambda x: x.get('bandwidth', 0))
    
    # 如果没有H.264，排除AV1
    valid_streams = [v for v in highest_streams if 'av01' not in v.get('codecs', '').lower()]
    if valid_streams:
        return max(valid_streams, key=lambda x: x.get('bandwidth', 0))
    
    # 返回最高画质的第一个
    return highest_streams[0]


async def download_video(bvid: str, output_dir: Optional[str] = None, auto_merge: bool = True, page_index: Optional[int] = None, threads: int = 3):
    """
    下载视频的完整流程

    Args:
        bvid: BV号
        output_dir: 输出目录（如果为None则使用当前工作目录的downloads文件夹）
        auto_merge: 是否自动合并音视频（默认True）
        page_index: 指定分P索引（None表示下载所有分P）
        threads: 并行下载的线程数（默认3）
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
    
    # 加载登录凭证
    credential = load_credential()
    
    # 验证凭证有效性
    if credential:
        print("\n[INFO] 正在验证登录凭证...")
        is_valid, is_vip, level = await verify_credential(credential)
        
        if not is_valid:
            print("\n" + "=" * 70)
            print("[WARNING] ⚠️ 登录凭证已失效！")
            print("=" * 70)
            print("[INFO] 请重新获取Cookie：")
            print("  1. 登录B站网页版 (https://www.bilibili.com)")
            print("  2. 按F12打开开发者工具")
            print("  3. 切换到Network(网络)标签")
            print("  4. 刷新页面")
            print("  5. 点击任意请求，复制Cookie值")
            print("  6. 更新配置文件:", os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'config.ini')))
            print("=" * 70)
            credential = None
        else:
            print(f"[INFO] ✓ 登录凭证有效 (用户等级: {level})")
            if is_vip:
                print("[INFO] ✓ 检测到大会员，可以下载1080P+高清画质")
    
    # 1. 获取视频信息
    print("\n[INFO] 获取视频信息...")
    v = video.Video(bvid=bvid, credential=credential)
    info = await v.get_info()
    
    title = info.get('title', 'unknown')
    owner = info.get('owner', {}).get('name', 'unknown')
    duration = info.get('duration', 0)
    
    print(f"[INFO] 标题: {title}")
    print(f"[INFO] UP主: {owner}")
    print(f"[INFO] 时长: {duration}秒")
    
    # 获取所有分P信息
    pages = info.get('pages', [])
    print(f"[INFO] 共有 {len(pages)} 个分P")
    
    # 确定要下载的分P列表
    if page_index is not None:
        if page_index < 0 or page_index >= len(pages):
            print(f"[ERROR] 无效的分P索引: {page_index}")
            return False
        page_list = [page_index]
    else:
        page_list = list(range(len(pages)))
    
    print(f"[INFO] 将下载 {len(page_list)} 个视频")
    
    # 创建主输出目录
    os.makedirs(output_dir, exist_ok=True)
    # 文件夹命名：时间戳+原始标题
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    safe_title = re.sub(r'[\\/:*?"<>|]', '', title)
    safe_title = safe_title.strip()
    # 截取标题前30字符
    if len(safe_title) > 30:
        safe_title = safe_title[:30].strip()
    main_output_dir = os.path.join(output_dir, f"{timestamp}{safe_title}")
    os.makedirs(main_output_dir, exist_ok=True)
    
    # 2. 下载每个分P
    total_pages = len(page_list)
    
    # 显示线程数信息
    if total_pages > 1:
        print(f"[INFO] 将使用 {min(threads, total_pages)} 个线程并行下载 {total_pages} 个视频")
    
    async def download_single_video(idx: int, page_idx: int, semaphore: asyncio.Semaphore, max_retries: int = 3) -> tuple:
        """下载单个视频的异步函数，支持重试"""
        page_info = pages[page_idx]
        page_title = page_info.get('part', f'P{page_idx + 1}')
        error_msg = "未知错误"
        
        for retry_count in range(max_retries):
            async with semaphore:
                success = True
                error_msg = ""
                
                try:
                    retry_prefix = f"[重试 {retry_count + 1}/{max_retries}]" if retry_count > 0 else ""
                    print(f"\n{'='*70}")
                    print(f"{retry_prefix}[INFO] 下载第 {idx}/{total_pages} 个视频 (分P {page_idx + 1}): {page_title}")
                    print(f"{'='*70}")
                    
                    if retry_count > 0:
                        print(f"[INFO] 等待3秒后重试...")
                        await asyncio.sleep(3)
                    
                    # 获取下载链接
                    download_info = await v.get_download_url(page_index=page_idx)
                    
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
                                    'codecs': v_stream.get('codecs', ''),
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
                        success = False
                        error_msg = "未找到下载链接"
                        if retry_count < max_retries - 1:
                            continue
                        return success, error_msg
                    
                    # 分离音视频
                    video_streams = [u for u in urls if u['type'] == 'video']
                    audio_streams = [u for u in urls if u['type'] == 'audio']
                    
                    if not video_streams or not audio_streams:
                        success = False
                        error_msg = "未找到完整的音视频流"
                        if retry_count < max_retries - 1:
                            continue
                        return success, error_msg
                    
                    # 选择最佳视频流
                    best_video = select_best_video_stream(urls)
                    
                    if not best_video:
                        success = False
                        error_msg = "无法选择有效的视频流"
                        if retry_count < max_retries - 1:
                            continue
                        return success, error_msg
                    
                    best_audio = max(audio_streams, key=lambda x: x['bandwidth'])
                    
                    quality_name = get_quality_name(best_video.get('quality', 0))
                    print(f"[INFO] 视频画质: {quality_name} (ID: {best_video.get('quality', 0)})")
                    print(f"[INFO] 视频编码: {best_video.get('codecs', 'unknown')}")
                    
                    # 准备文件名（格式：01.标题.mp4）
                    page_num = page_idx + 1
                    safe_page_title = re.sub(r'[\\/:*?"<>|，。（）()！!]', '', page_title)
                    safe_page_title = safe_page_title.strip()
                    if len(safe_page_title) > 30:
                        safe_page_title = safe_page_title[:30].strip()
                    safe_page_title = re.sub(r'^\d+[\.．]', '', safe_page_title)
                    p_safe_title = f"{page_num:02d}.{safe_page_title}"
                    
                    # 下载视频
                    video_filename = f"{p_safe_title}_video.mp4"
                    video_path = os.path.join(main_output_dir, video_filename)
                    
                    print(f"[INFO] 下载视频...")
                    if not download_file(best_video['url'], video_path):
                        success = False
                        error_msg = "下载视频失败"
                        if retry_count < max_retries - 1:
                            continue
                        return success, error_msg
                    
                    # 下载音频
                    audio_filename = f"{p_safe_title}_audio.m4a"
                    audio_path = os.path.join(main_output_dir, audio_filename)
                    
                    print(f"[INFO] 下载音频...")
                    if not download_file(best_audio['url'], audio_path):
                        success = False
                        error_msg = "下载音频失败"
                        if retry_count < max_retries - 1:
                            continue
                        return success, error_msg
                    
                    # 合并音视频
                    final_filename = f"{p_safe_title}.mp4"
                    final_path = os.path.join(main_output_dir, final_filename)
                    
                    if auto_merge and ffmpeg_path:
                        merge_success = merge_video_audio(video_path, audio_path, final_path, ffmpeg_path)
                        if merge_success:
                            print(f"✓ 分P {page_idx + 1} 下载完成: {final_filename}")
                        else:
                            print(f"✓ 分P {page_idx + 1} 下载完成（未合并）: {video_filename}, {audio_filename}")
                    else:
                        print(f"✓ 分P {page_idx + 1} 下载完成: {video_filename}, {audio_filename}")
                    
                    return success, error_msg
                    
                except Exception as e:
                    print(f"[ERROR] 下载分P {page_idx + 1} 失败: {e}")
                    import traceback
                    traceback.print_exc()
                    error_msg = str(e)
                    if retry_count < max_retries - 1:
                        print(f"[INFO] 将在3秒后进行第{retry_count + 2}次重试...")
                        await asyncio.sleep(3)
                        continue
                    return False, error_msg
        
        return False, error_msg
    
    # 创建信号量限制并发数
    semaphore = asyncio.Semaphore(min(threads, total_pages))
    
    # 创建所有下载任务
    tasks = []
    for idx, page_idx in enumerate(page_list, 1):
        task = download_single_video(idx, page_idx, semaphore)
        tasks.append(task)
    
    # 并行执行所有任务
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 统计结果
    success_count = 0
    fail_count = 0
    
    for i, result in enumerate(results):
        if isinstance(result, tuple) and result[0]:
            success_count += 1
        else:
            fail_count += 1
    
    # 3. 完成总结
    print(f"\n{'='*70}")
    print("下载完成！")
    print("=" * 70)
    print(f"总视频数: {total_pages}")
    print(f"成功下载: {success_count}")
    print(f"失败数量: {fail_count}")
    print(f"保存目录: {main_output_dir}")
    print("=" * 70)
    
    return success_count > 0


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
  python scripts/download.py "BV1mZrKBAEHf" --page 0  # 只下载第1个分P

说明:
  本脚本使用bilibili-api库直接从B站API下载视频
  自动下载音视频并使用ffmpeg合并
  如果未安装ffmpeg，将提供合并命令
  支持登录后下载高清画质（需配置config.ini）
        """
    )
    
    parser.add_argument('url', help='Bilibili视频链接或BV号')
    parser.add_argument('-o', '--output', default=None, help='下载输出目录 (默认: 当前工作目录下的downloads文件夹)')
    parser.add_argument('--no-merge', action='store_true', help='禁用自动合并音视频')
    parser.add_argument('--page', type=int, default=None, help='指定下载的分P编号（从0开始），不指定则下载所有分P')
    parser.add_argument('--threads', type=int, default=3, help='并行下载的线程数 (默认: 3)')
    
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
    success = await download_video(bvid, output_dir, auto_merge, page_index=args.page, threads=args.threads)
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
