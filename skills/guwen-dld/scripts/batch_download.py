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
import concurrent.futures
from urllib.parse import urljoin
from queue import Queue

thread_local = threading.local()

def get_session():
    """获取线程本地session"""
    if not hasattr(thread_local, 'session'):
        thread_local.session = requests.Session()
        thread_local.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    return thread_local.session

def extract_intro(html):
    """从首页提取书籍简介"""
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
    """从章节页面提取正文内容"""
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    html = re.sub(r'<div[^>]*class="[^"]*play[^"]*"[^>]*>.*?</div>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<div[^>]*class="[^"]*nav[^"]*"[^>]*>.*?</div>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<div[^>]*class="[^"]*footer[^"]*"[^>]*>.*?</div>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<div[^>]*class="[^"]*menu[^"]*"[^>]*>.*?</div>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<div[^>]*class="[^"]*tool[^"]*"[^>]*>.*?</div>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<audio[^>]*>.*?</audio>', '', html, flags=re.DOTALL)
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
    """从目录页解析所有章节链接"""
    pattern = r'href="(/guwen/bookv_[^"]+\.aspx)"'
    matches = re.findall(pattern, html)
    
    chapters = []
    for match in matches:
        full_url = urljoin(base_url, match)
        if full_url not in chapters:
            chapters.append(full_url)
    return chapters

def download_one_book(url, output_dir, lock, result_queue):
    """下载单本古籍"""
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
            result_queue.put((filename, 1, True))
            return filename, 1
        else:
            all_content = []
            for i, chapter_url in enumerate(chapters):
                time.sleep(0.3)
                try:
                    resp = session.get(chapter_url, timeout=30)
                    resp.encoding = 'utf-8'
                    chapter_html = resp.text
                    content = extract_content(chapter_html)
                    if content:
                        all_content.append(content)
                except Exception as e:
                    pass
            
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                if intro_content:
                    f.write(intro_content)
                    f.write("\n" + "="*50 + "\n\n")
                for content in all_content:
                    f.write(content)
                    f.write('\n\n---章节分隔---\n\n')
            
            result_queue.put((filename, len(all_content), True))
            return filename, len(all_content)
            
    except Exception as e:
        result_queue.put((url, 0, False))
        return None, 0

def worker(url_queue, output_dir, lock, result_queue, thread_id):
    """工作线程"""
    while True:
        try:
            url = url_queue.get_nowait()
        except:
            break
        
        filename, count, success = download_one_book(url, output_dir, lock, result_queue)
        if success:
            with lock:
                print(f"[线程{thread_id}] 完成: {filename} ({count}章节)")
        else:
            with lock:
                print(f"[线程{thread_id}] 失败: {url}")
        
        url_queue.task_done()
        time.sleep(0.5)  # 避免请求过快

def batch_download_parallel(max_workers=5, max_books=None):
    """并行批量下载"""
    output_dir = os.getcwd()
    guwen_dir = os.path.join(output_dir, "guwen_books")
    os.makedirs(guwen_dir, exist_ok=True)
    
    urls_file = os.path.join(guwen_dir, "all_urls.txt")
    if not os.path.exists(urls_file):
        print("请先运行 --urls-only 获取URL列表")
        return
    
    with open(urls_file, 'r', encoding='utf-8') as f:
        all_urls = [line.strip() for line in f if line.strip()]
    
    print(f"共 {len(all_urls)} 本古籍，使用 {max_workers} 线程并行下载...")
    
    if max_books:
        all_urls = all_urls[:max_books]
    
    url_queue = Queue()
    for url in all_urls:
        url_queue.put(url)
    
    lock = threading.Lock()
    result_queue = Queue()
    
    threads = []
    for i in range(max_workers):
        t = threading.Thread(target=worker, args=(url_queue, guwen_dir, lock, result_queue, i+1))
        t.daemon = True
        t.start()
        threads.append(t)
    
    url_queue.join()
    
    success = 0
    failed = 0
    while not result_queue.empty():
        filename, count, success_flag = result_queue.get()
        if success_flag:
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