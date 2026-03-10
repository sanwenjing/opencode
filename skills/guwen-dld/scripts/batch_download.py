# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import re
import time
import json
import requests
import threading
from urllib.parse import urljoin
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed

thread_local = threading.local()

def get_session():
    if not hasattr(thread_local, 'session'):
        thread_local.session = requests.Session()
        thread_local.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    return thread_local.session

def extract_intro(html):
    desc_match = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]+)"', html)
    if desc_match:
        intro = desc_match.group(1).strip()
        if intro and len(intro) > 10:
            title_match = re.search(r'<title>([^<]+)</title>', html)
            title = ""
            if title_match:
                title = title_match.group(1).replace('全文_古文岛_原古诗文网', '').replace('古文岛', '').replace('原古诗文网', '').strip()
            result = ""
            if title:
                result += title + "\n\n"
            result += "【简介】" + intro + "\n\n"
            return result
    return ""

def extract_content(html):
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    html = re.sub(r'<div[^>]*class="[^"]*play[^"]*"[^>]*>.*?</div>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<div[^>]*class="[^"]*nav[^"]*"[^>]*>.*?</div>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<div[^>]*class="[^"]*footer[^"]*"[^>]*>.*?</div>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<div[^>]*class="[^"]*menu[^"]*"[^>]*>.*?</div>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<div[^>]*class="[^"]*tool[^"]*"[^>]*>.*?</div>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<audio[^>]*>.*? ', '', html, flags=re.DOTALL)
    html = re.sub(r'<span[^>]*class="[^"]*speaker[^"]*"[^>]*>.*?</span>', '', html, flags=re.DOTALL)
    html = re.sub(r'<a[^>]*>.*?</a>', '', html, flags=re.DOTALL)
    html = re.sub(r'<button[^>]*>.*?</button>', '', html, flags=re.DOTALL)
    
    html = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'</p>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'</div>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'</h[1-6]>', '\n', html, flags=re.IGNORECASE)
    
    text = re.sub(r'<[^>]+>', '', html)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'APP|登录|推荐|诗文|名句古籍作者字词', '', text)
    text = re.sub(r'东北一枝花|张哈哈|朗诵|琼花', '', text)
    text = re.sub(r'\d{1,2}:\d{2}\s*/\s*\d{1,2}:\d{2}', '', text)
    text = re.sub(r'0\.25x|0\.5x|0\.75x|1\.0x|1\.25x|1\.5x|2\.0x', '', text)
    text = re.sub(r'播放列表|单曲循环|列表循环|随机播放|单曲播放', '', text)
    text = re.sub(r'古文岛|古诗文网|原古网', '', text)
    text = re.sub(r'__+', '', text)
    text = re.sub(r'^\s*[\d（）()]+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[\u4e00-\u9fa5]{1,2}\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[（:——]+\s*$', '', text, flags=re.MULTILINE)
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)

def parse_chapters(html, base_url):
    chapters = set()
    base_url = base_url.rstrip('/')
    
    pattern1 = r'href="(/guwen/bookv_[^"]+\.aspx)"'
    for match in re.findall(pattern1, html):
        full_url = urljoin(base_url, match)
        chapters.add(full_url)
    
    pattern2 = r'href="(/guwen/book_[^"]+\.aspx)"'
    for match in re.findall(pattern2, html):
        full_url = urljoin(base_url, match)
        chapters.add(full_url)
    
    return list(chapters)

def download_chapter(args):
    chapter_url, session = args
    try:
        resp = session.get(chapter_url, timeout=30)
        resp.encoding = 'utf-8'
        content = extract_content(resp.text)
        return content if content else None
    except Exception:
        return None

def download_one_book(url, output_dir, lock):
    session = get_session()
    try:
        response = session.get(url, timeout=30)
        response.encoding = 'utf-8'
        html = response.text
        
        title_match = re.search(r'<title>([^<]+)</title>', html)
        if title_match:
            title = title_match.group(1).replace('全文_古文岛_原古诗文网', '').strip()
            title = re.sub(r'[\\/\:\*\?"<>\|]', '', title)
            filename = f"{title}.txt"
        else:
            book_id = re.search(r'book_([^.]+)\.aspx', url)
            filename = f"guwen_{book_id.group(1)}.txt" if book_id else "unknown.txt"
        
        intro_content = extract_intro(html)
        chapters = parse_chapters(html, url)
        
        if not chapters:
            content = extract_content(html)
            if intro_content:
                content = intro_content + "\n\n" + content
            
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            with lock:
                print(f"  [完成] {filename} (单页)")
            return filename, 1, True
        else:
            all_content = []
            chapter_count = len(chapters)
            with ThreadPoolExecutor(max_workers=10) as executor:
                args_list = [(url, session) for url in chapters]
                results = list(executor.map(download_chapter, args_list))
                for i, content in enumerate(results):
                    if content:
                        all_content.append(content)
            
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                if intro_content:
                    f.write(intro_content)
                    f.write("\n" + "=" * 50 + "\n\n")
                for content in all_content:
                    f.write(content)
                    f.write('\n\n---章节分隔---\n\n')
            
            with lock:
                print(f"  [完成] {filename} ({len(all_content)}/{chapter_count}章节)")
            return filename, len(all_content), True
            
    except Exception as e:
        with lock:
            print(f"  [失败] {url}")
        return None, 0, False

def batch_download_parallel(max_workers=5, max_books=None):
    output_dir = os.getcwd()
    guwen_dir = os.path.join(output_dir, "guwen_books")
    os.makedirs(guwen_dir, exist_ok=True)
    
    urls_file = os.path.join(guwen_dir, "all_urls.txt")
    if not os.path.exists(urls_file):
        print("错误: 未找到 all_urls.txt，请先运行 get_all_urls.py 获取URL列表")
        return
    
    with open(urls_file, 'r', encoding='utf-8') as f:
        all_urls = [line.strip() for line in f if line.strip()]
    
    print(f"共 {len(all_urls)} 本古籍，使用 {max_workers} 线程并行下载...")
    
    if max_books:
        all_urls = all_urls[:max_books]
    
    lock = threading.Lock()
    success = 0
    failed = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_one_book, url, guwen_dir, lock): url for url in all_urls}
        for future in as_completed(futures):
            filename, count, ok = future.result()
            if ok:
                success += 1
            else:
                failed += 1
    
    print(f"\n下载完成! 成功: {success}, 失败: {failed}")
    print(f"文件保存位置: {guwen_dir}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='并行批量下载古文岛古籍')
    parser.add_argument('--workers', type=int, default=5, help='线程数')
    parser.add_argument('--max', type=int, default=None, help='最大下载数量')
    
    args = parser.parse_args()
    batch_download_parallel(args.workers, args.max)