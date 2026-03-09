# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import re
import argparse
import json
from urllib.parse import urljoin

def load_config():
    """加载配置文件"""
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(skill_dir, "config", "config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"default_encoding": "utf-8"}

def fetch_chapter(url, session):
    """获取单个章节内容"""
    import requests
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = session.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        print(f"获取章节失败 {url}: {e}")
        return None

def parse_chapters_from_index(html, base_url):
    """从目录页解析所有章节链接"""
    pattern = r'href="(/guwen/bookv_[^"]+\.aspx)"'
    matches = re.findall(pattern, html)
    
    chapters = []
    for match in matches:
        full_url = urljoin(base_url, match)
        if full_url not in chapters:
            chapters.append(full_url)
    return chapters

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

def fetch_and_combine(url, output_path, encoding='utf-8'):
    """主函数：获取所有章节并合并"""
    import requests
    
    print(f"正在获取目录页: {url}")
    
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = session.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        index_html = response.text
    except Exception as e:
        print(f"获取目录页失败: {e}")
        return False
    
    intro_content = extract_intro(index_html)
    if intro_content:
        print("已提取书籍简介")
    
    chapters = parse_chapters_from_index(index_html, url)
    print(f"找到 {len(chapters)} 个章节")
    
    if not chapters:
        content = extract_content(index_html)
        with open(output_path, 'w', encoding=encoding) as f:
            if intro_content:
                f.write(intro_content)
            f.write(content)
        print(f"文件已保存到: {os.path.abspath(output_path)}")
        return True
    
    all_content = []
    for i, chapter_url in enumerate(chapters, 1):
        print(f"正在获取第 {i}/{len(chapters)} 章: {chapter_url}")
        html = fetch_chapter(chapter_url, session)
        if html:
            content = extract_content(html)
            if content:
                all_content.append(content)
    
    with open(output_path, 'w', encoding=encoding) as f:
        if intro_content:
            f.write(intro_content)
            f.write("\n" + "="*50 + "\n\n")
        
        for content in all_content:
            f.write(content)
            f.write('\n\n---章节分隔---\n\n')
    
    print(f"\n完成! 共获取 {len(all_content)} 个章节")
    print(f"文件已保存到: {os.path.abspath(output_path)}")
    return True

def main():
    parser = argparse.ArgumentParser(description='下载并拼接TXT书籍')
    parser.add_argument('--url', '-u', help='目录页URL', required=True)
    parser.add_argument('--output', '-o', help='输出文件路径', default='output.txt')
    parser.add_argument('--encoding', '-e', help='输出文件编码', default='utf-8')
    
    args = parser.parse_args()
    
    config = load_config()
    encoding = args.encoding or config.get('default_encoding', 'utf-8')
    
    output_dir = os.getcwd()
    output_path = os.path.join(output_dir, args.output)
    
    fetch_and_combine(args.url, output_path, encoding)

if __name__ == '__main__':
    main()