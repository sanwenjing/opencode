# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import argparse
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup, Tag
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue


class RecursiveDownloader:
    def __init__(self, base_url, output_dir, delay=0.5, timeout=30, max_workers=50):
        self.base_url = base_url
        self.output_dir = output_dir
        self.delay = delay
        self.timeout = timeout
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.downloaded_files = 0
        self.skipped_files = 0
        self.failed_files = 0
        self.lock = threading.Lock()
        self.file_queue = Queue()
        self.visited_urls = set()
        self.visited_lock = threading.Lock()
        self.expected_files = []  # 记录所有预期下载的文件

    def download_file(self, url, local_path):
        try:
            if os.path.exists(local_path):
                print(f"  跳过（已存在）: {os.path.basename(local_path)}")
                with self.lock:
                    self.skipped_files += 1
                return True

            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()

            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"  ✓ 下载成功: {os.path.basename(local_path)}")
            with self.lock:
                self.downloaded_files += 1
            return True

        except Exception as e:
            print(f"  ✗ 下载失败: {os.path.basename(local_path)} - {str(e)}")
            with self.lock:
                self.failed_files += 1
            return False

    def is_valid_url(self, url):
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https')

    def should_download(self, url):
        parsed = urlparse(url)
        base_parsed = urlparse(self.base_url)
        return parsed.netloc == base_parsed.netloc and parsed.path.startswith(base_parsed.path)

    def get_links(self, url):
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            links = []
            for a_tag in soup.find_all('a', href=True):
                if isinstance(a_tag, Tag):
                    href = a_tag.get('href')
                    if href and isinstance(href, str):
                        # 跳过上级目录链接和根目录链接
                        if href in ['../', '/']:
                            continue
                        full_url = urljoin(url, href)
                        
                        if self.should_download(full_url):
                            links.append(full_url)

            return links
        except Exception as e:
            print(f"  获取链接失败: {url} - {str(e)}")
            return []

    def get_relative_path(self, url):
        """获取相对于基础URL的路径
        
        强制保留完整的远程目录层级结构，包括主机名。
        例如： https://example.com/path/to/file.txt 将保存为 example.com/path/to/file.txt
        """
        parsed = urlparse(url)
        
        # 保留完整的远程目录结构：主机名 + 完整路径
        host = parsed.netloc
        path = parsed.path.lstrip('/')
        if not path:
            path = 'index.html'
        # 使用 / 作为分隔符，然后统一转换为系统路径
        relative_path = os.path.join(host.replace('/', os.sep), path.replace('/', os.sep))
        
        return relative_path

    def is_directory(self, url):
        parsed = urlparse(url)
        return parsed.path.endswith('/')

    def process_directory(self, url):
        """处理单个目录，将文件添加到下载队列"""
        with self.visited_lock:
            if url in self.visited_urls:
                return
            self.visited_urls.add(url)

        if not self.should_download(url):
            return

        print(f"[扫描] {url}")
        try:
            links = self.get_links(url)
            
            for link in links:
                if self.is_directory(link):
                    # 递归处理子目录
                    time.sleep(self.delay)
                    self.process_directory(link)
                else:
                    # 将文件添加到下载队列
                    relative_path = self.get_relative_path(link)
                    local_path = os.path.join(self.output_dir, relative_path)
                    self.file_queue.put((link, local_path))
                    # 记录预期下载的文件
                    with self.lock:
                        self.expected_files.append(local_path)
        except Exception as e:
            print(f"  扫描目录失败: {url} - {str(e)}")

    def start_download_workers(self):
        """启动下载工作线程"""
        def worker():
            while True:
                try:
                    url, local_path = self.file_queue.get(timeout=5)
                    if url is None:  # 结束信号
                        self.file_queue.task_done()
                        break
                    self.download_file(url, local_path)
                    self.file_queue.task_done()
                except Exception as e:
                    # 超时或其他错误，继续循环
                    continue

        threads = []
        for i in range(self.max_workers):
            t = threading.Thread(target=worker, name=f"DownloadWorker-{i}")
            t.daemon = True
            t.start()
            threads.append(t)
        
        return threads

    def verify_downloads(self):
        """校验下载的文件完整性"""
        print("\n" + "=" * 50)
        print("开始文件完整性校验...")
        print("=" * 50)
        
        # 获取预期文件总数
        total_expected = len(self.expected_files)
        
        # 获取本地实际存在的文件数
        local_files = []
        for root, dirs, files in os.walk(self.output_dir):
            for file in files:
                full_path = os.path.join(root, file)
                local_files.append(full_path)
        
        total_local = len(local_files)
        
        # 计算应该拥有的文件数（成功下载 + 已存在）
        expected_local_count = self.downloaded_files + self.skipped_files
        
        print(f"远程文件总数: {total_expected}")
        print(f"本地文件总数: {total_local}")
        print(f"成功下载: {self.downloaded_files}")
        print(f"跳过（已存在）: {self.skipped_files}")
        print(f"失败: {self.failed_files}")
        print(f"预期本地应有: {expected_local_count}")
        
        # 检查差异
        if total_local == expected_local_count and self.failed_files == 0:
            print("\n✓ 文件完整性校验通过！所有文件下载完整。")
            return True
        else:
            print("\n✗ 文件完整性校验未通过！")
            
            # 找出缺失的文件
            missing_files = []
            for expected_file in self.expected_files:
                if not os.path.exists(expected_file):
                    missing_files.append(expected_file)
            
            if missing_files:
                print(f"\n缺失文件列表（共 {len(missing_files)} 个）:")
                for i, missing in enumerate(missing_files[:20], 1):  # 只显示前20个
                    print(f"  {i}. {os.path.basename(missing)}")
                if len(missing_files) > 20:
                    print(f"  ... 还有 {len(missing_files) - 20} 个文件未显示")
            
            # 检查是否有额外的文件
            expected_set = set(self.expected_files)
            extra_files = [f for f in local_files if f not in expected_set]
            if extra_files:
                print(f"\n额外文件（不在远程目录中）: {len(extra_files)} 个")
            
            return False

    def run(self):
        print(f"开始递归下载...")
        print(f"目标URL: {self.base_url}")
        print(f"输出目录: {self.output_dir}")
        print(f"目录结构: 强制保留完整层级（包括主机名）")
        print(f"延迟: {self.delay}秒")
        print(f"线程数: {self.max_workers}")
        print("-" * 50)

        os.makedirs(self.output_dir, exist_ok=True)
        
        # 启动下载工作线程
        download_threads = self.start_download_workers()
        
        # 扫描目录结构（单线程，避免服务器压力）
        print("\n扫描目录结构中...")
        try:
            self.process_directory(self.base_url)
        except Exception as e:
            print(f"扫描过程出错: {str(e)}")
        
        # 等待队列处理完成
        print(f"\n等待下载完成，文件数量: {self.file_queue.qsize()}...")
        self.file_queue.join()
        
        # 发送结束信号给所有工作线程
        for _ in range(self.max_workers):
            self.file_queue.put((None, None))
        
        # 停止下载工作线程
        print("正在关闭下载线程...")
        for t in download_threads:
            t.join(timeout=2.0)

        print("-" * 50)
        print(f"下载完成!")
        print(f"成功: {self.downloaded_files} 个文件")
        print(f"跳过: {self.skipped_files} 个文件（已存在）")
        print(f"失败: {self.failed_files} 个文件")
        
        # 执行文件完整性校验
        self.verify_downloads()


def main():
    parser = argparse.ArgumentParser(
        description='递归下载镜像站点文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  # 下载默认的阿里云Alpine镜像（默认50线程）
  python download.py
  
  # 下载指定URL
  python download.py -u https://mirrors.aliyun.com/alpine/v3.22/
  
  # 指定输出目录
  python download.py -u https://example.com/repo/ -o ./my-downloads
  
  # 设置下载延迟（避免请求过快）
  python download.py -u https://example.com/ -d 1.0
  
  # 设置并发线程数（默认50，可根据网络调整）
  python download.py -u https://example.com/ -w 100
  
  # 注意：强制保留完整的远程目录层级结构（包括主机名）
  # 例如：下载 https://example.com/repo/ 将保存到 downloads/example.com/repo/...
        '''
    )
    
    parser.add_argument(
        '-u', '--url',
        default='https://mirrors.aliyun.com/alpine/v3.23/',
        help='要下载的基础URL (默认: https://mirrors.aliyun.com/alpine/v3.23/)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='downloads',
        help='输出目录路径 (默认: 当前目录下的downloads文件夹)'
    )
    
    parser.add_argument(
        '-d', '--delay',
        type=float,
        default=0.5,
        help='每次请求之间的延迟（秒）(默认: 0.5)'
    )
    
    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=30,
        help='请求超时时间（秒）(默认: 30)'
    )
    
    parser.add_argument(
        '-w', '--workers',
        type=int,
        default=50,
        help='并发下载线程数 (默认: 50)'
    )

    args = parser.parse_args()

    # 确保输出目录是基于当前工作目录的绝对路径
    if os.path.isabs(args.output):
        output_dir = args.output
    else:
        output_dir = os.path.join(os.getcwd(), args.output)

    downloader = RecursiveDownloader(
        base_url=args.url,
        output_dir=output_dir,
        delay=args.delay,
        timeout=args.timeout,
        max_workers=args.workers
    )
    
    downloader.run()


if __name__ == '__main__':
    main()
