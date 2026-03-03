# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import re
import json
import argparse
import requests
from datetime import datetime
from bs4 import BeautifulSoup

PATH_SEP = os.sep


def load_config():
    config_path = os.path.join(os.getcwd(), "config", "config.json")
    if not os.path.exists(config_path):
        skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(skill_dir, "config", "config.json")
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def fetch_weibo_hot(keyword='', max_news=20):
    news_list = []
    try:
        url = 'https://weibo.com/ajax/side/hotSearch'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://weibo.com'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        data = response.json()
        
        realtime = data.get('data', {}).get('realtime', [])
        
        if keyword:
            for item in realtime:
                word = item.get('word', '')
                if keyword.lower() in word.lower():
                    news_list.append({
                        'title': word,
                        'url': f'https://s.weibo.com/weibo?q={word}',
                        'source': '微博',
                        'time': '',
                        'hot': item.get('num', '')
                    })
        else:
            for item in realtime[:max_news]:
                news_list.append({
                    'title': item.get('word', ''),
                    'url': f'https://s.weibo.com/weibo?q={item.get("word", "")}',
                    'source': '微博',
                    'time': '',
                    'hot': item.get('num', '')
                })
    except Exception as e:
        print(f"获取微博热搜失败: {e}")
    return news_list


def fetch_toutiao_hot(keyword='', max_news=20):
    news_list = []
    try:
        url = 'https://www.toutiao.com/api/pc/feed/?category=news_hot&max_behot_time=0'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.toutiao.com'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        data = response.json()
        
        articles = data.get('data', [])
        
        if keyword:
            for item in articles:
                title = item.get('title', '')
                if keyword.lower() in title.lower():
                    news_list.append({
                        'title': title,
                        'url': 'https://www.toutiao.com' + item.get('source_url', ''),
                        'source': '今日头条',
                        'time': '',
                        'hot': ''
                    })
        else:
            for item in articles[:max_news]:
                news_list.append({
                    'title': item.get('title', ''),
                    'url': 'https://www.toutiao.com' + item.get('source_url', ''),
                    'source': '今日头条',
                    'time': '',
                    'hot': ''
                })
    except Exception as e:
        print(f"获取今日头条热搜失败: {e}")
    return news_list


def fetch_baidu_finance(keyword='', max_news=20):
    news_list = []
    try:
        url = 'https://top.baidu.com/board?tab=finance'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        match = re.search(r'\"data\":\s*(\[.*?\])\s*,', response.text, re.DOTALL)
        if match:
            data = json.loads(match.group(1))
            
            if keyword:
                for item in data:
                    word = item.get('word', '')
                    if keyword.lower() in word.lower():
                        news_list.append({
                            'title': word,
                            'url': item.get('url', ''),
                            'source': '百度财经',
                            'time': '',
                            'hot': item.get('hotScore', '')
                        })
            else:
                for item in data[:max_news]:
                    news_list.append({
                        'title': item.get('word', ''),
                        'url': item.get('url', ''),
                        'source': '百度财经',
                        'time': '',
                        'hot': item.get('hotScore', '')
                    })
    except Exception as e:
        print(f"获取百度财经榜失败: {e}")
    return news_list


def fetch_all_news(keyword='', max_news=20):
    all_news = []
    
    print("正在获取微博热搜...")
    weibo_news = fetch_weibo_hot(keyword, max_news)
    all_news.extend(weibo_news)
    print(f"微博: {len(weibo_news)} 条")
    
    if len(all_news) < max_news:
        print("正在获取今日头条热搜...")
        toutiao_news = fetch_toutiao_hot(keyword, max_news - len(all_news))
        all_news.extend(toutiao_news)
        print(f"今日头条: {len(toutiao_news)} 条")
    
    if len(all_news) < max_news and not keyword:
        print("正在获取百度财经榜...")
        baidu_news = fetch_baidu_finance(keyword, max_news - len(all_news))
        all_news.extend(baidu_news)
        print(f"百度财经: {len(baidu_news)} 条")
    
    return all_news[:max_news]


def format_json(news_list):
    result = {
        'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total': len(news_list),
        'news': news_list
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def format_markdown(news_list):
    md = f"# 财经新闻汇总\n\n"
    md += f"获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md += f"共获取 {len(news_list)} 条新闻\n\n---\n\n"
    
    for i, news in enumerate(news_list, 1):
        md += f"### {i}. {news['title']}\n\n"
        md += f"- 来源: {news['source']}\n"
        if news.get('hot'):
            md += f"- 热度: {news['hot']}\n"
        if news.get('time'):
            md += f"- 时间: {news['time']}\n"
        if news.get('url'):
            md += f"- 链接: {news['url']}\n"
        md += "\n"
    
    return md


def main():
    parser = argparse.ArgumentParser(description='财经新闻获取工具')
    parser.add_argument('--keyword', '-k', default='', help='搜索关键词')
    parser.add_argument('--source', '-s', default='all', 
                        choices=['all', 'weibo', 'toutiao', 'baidu'], 
                        help='新闻源 (默认: all)')
    parser.add_argument('--format', '-f', default='json',
                        choices=['json', 'markdown'], 
                        help='输出格式 (默认: json)')
    parser.add_argument('--output', '-o', default='', 
                        help='输出文件路径 (为空则输出到 stdout)')
    parser.add_argument('--max', '-m', type=int, default=20, 
                        help='最大新闻数量 (默认: 20)')
    
    args = parser.parse_args()
    
    keyword = args.keyword
    
    print(f"正在获取财经新闻...")
    if keyword:
        print(f"关键词: {keyword}")
    print(f"来源: {args.source}")
    print("-" * 40)
    
    if args.source == 'all':
        news_list = fetch_all_news(keyword, args.max)
    elif args.source == 'weibo':
        news_list = fetch_weibo_hot(keyword, args.max)
    elif args.source == 'toutiao':
        news_list = fetch_toutiao_hot(keyword, args.max)
    elif args.source == 'baidu':
        news_list = fetch_baidu_finance(keyword, args.max)
    else:
        news_list = []
    
    print("-" * 40)
    print(f"共获取到 {len(news_list)} 条新闻")
    
    if args.format == 'json':
        output = format_json(news_list)
    else:
        output = format_markdown(news_list)
    
    if args.output:
        output_path = os.path.join(os.getcwd(), args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"新闻已保存到: {output_path}")
    else:
        print(output)


if __name__ == '__main__':
    main()
