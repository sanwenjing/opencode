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
import tarfile
import io
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue


def get_packages_from_index(index_url, timeout=60):
    """从APKINDEX.tar.gz获取包列表"""
    try:
        response = requests.get(index_url, timeout=timeout)
        if response.status_code == 200:
            tar = tarfile.open(fileobj=io.BytesIO(response.content), mode='r:gz')
            for member in tar.getmembers():
                if 'APKINDEX' in member.name:
                    f = tar.extractfile(member)
                    content = f.read().decode('utf-8', errors='ignore')
                    packages = set()
                    current_pkg = {}
                    for line in content.split('\n'):
                        if line.startswith('P:'):
                            current_pkg['name'] = line[2:]
                        elif line.startswith('V:'):
                            current_pkg['version'] = line[2:]
                        elif line == '' and current_pkg:
                            if 'name' in current_pkg:
                                packages.add(f"{current_pkg['name']}-{current_pkg['version']}.apk")
                            current_pkg = {}
                    return packages
    except Exception as e:
        print(f"  获取APKINDEX失败: {e}")
    return set()


def get_remote_package_list(base_url, arch='x86_64'):
    """获取远程APK包列表（从APKINDEX）"""
    main_index = f"{base_url}/main/{arch}/APKINDEX.tar.gz"
    community_index = f"{base_url}/community/{arch}/APKINDEX.tar.gz"

    main_pkgs = get_packages_from_index(main_index)
    community_pkgs = get_packages_from_index(community_index)

    return {
        'main': main_pkgs,
        'community': community_pkgs,
        'main_total': len(main_pkgs),
        'community_total': len(community_pkgs)
    }


def get_local_packages(output_dir, base_url, arch='x86_64'):
    """获取本地已下载的包，返回 {main/x86_64/xxx.apk, community/x86_64/xxx.apk} 格式"""
    local_pkgs = set()
    host = urlparse(base_url).netloc

    for root, dirs, files in os.walk(output_dir):
        for f in files:
            if f.endswith('.apk'):
                full_path = os.path.join(root, f)
                try:
                    rel_path = os.path.relpath(full_path, output_dir)
                except ValueError:
                    continue
                parts = rel_path.split(os.sep)
                # 路径格式: host/alpine/v3.23/repo/arch/xxx.apk
                # 我们需要提取 repo (main 或 community)
                if len(parts) >= 5 and parts[0] == host:
                    repo = parts[3]  # main 或 community
                    if repo in ['main', 'community']:
                        rel_pkg_path = f"{repo}/{arch}/{f}"
                        local_pkgs.add(rel_pkg_path)

    return local_pkgs


def compare_and_report(local_pkgs, remote_info, base_url, arch='x86_64'):
    """对比本地和远程包，返回缺失的包"""
    remote_main = {f'main/{arch}/{pkg}' for pkg in remote_info['main']}
    remote_community = {f'community/{arch}/{pkg}' for pkg in remote_info['community']}

    local_full = set()
    for pkg in local_pkgs:
        local_full.add(pkg)

    missing_main = remote_main - local_full
    missing_community = remote_community - local_full

    downloaded_main = remote_main & local_full
    downloaded_community = remote_community & local_full

    return {
        'remote_main': remote_info['main_total'],
        'remote_community': remote_info['community_total'],
        'local_main': len(downloaded_main),
        'local_community': len(downloaded_community),
        'missing_main': missing_main,
        'missing_community': missing_community,
        'missing_main_count': len(missing_main),
        'missing_community_count': len(missing_community)
    }


def download_missing_packages(missing_list, base_url, output_dir, max_workers=20, timeout=30):
    """下载缺失的包"""
    if not missing_list:
        print("没有需要下载的包")
        return 0, 0

    success = 0
    failed = 0
    failed_items = []

    def download_single(item):
        rel_path, filename = item
        if rel_path.startswith('main/'):
            repo_prefix = 'main'
        else:
            repo_prefix = 'community'
        url = f"{base_url}/{repo_prefix}/x86_64/{filename}"
        local_path = os.path.join(output_dir, rel_path)

        try:
            if os.path.exists(local_path):
                return True, '已存在'

            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            response = requests.get(url, timeout=timeout, stream=True)
            response.raise_for_status()

            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True, '成功'
        except Exception as e:
            return False, str(e)

    print(f"开始下载 {len(missing_list)} 个缺失包...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_single, item): item for item in missing_list}
        for i, future in enumerate(as_completed(futures)):
            ok, msg = future.result()
            if ok:
                success += 1
            else:
                failed += 1
            if (success + failed) % 500 == 0:
                print(f"  进度: {success + failed}/{len(missing_list)}")

    if failed > 0:
        print(f"  失败: {failed} 个")
    return success, failed


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
        self.expected_files = []

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

            print(f"  下载成功: {os.path.basename(local_path)}")
            with self.lock:
                self.downloaded_files += 1
            return True

        except Exception as e:
            print(f"  下载失败: {os.path.basename(local_path)} - {str(e)}")
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
        """获取相对于基础URL的路径"""
        parsed = urlparse(url)
        host = parsed.netloc
        path = parsed.path.lstrip('/')
        if not path:
            path = 'index.html'
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
                    time.sleep(self.delay)
                    self.process_directory(link)
                else:
                    relative_path = self.get_relative_path(link)
                    local_path = os.path.join(self.output_dir, relative_path)
                    self.file_queue.put((link, local_path))
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
                    if url is None:
                        self.file_queue.task_done()
                        break
                    self.download_file(url, local_path)
                    self.file_queue.task_done()
                except Exception as e:
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

        total_expected = len(self.expected_files)

        local_files = []
        for root, dirs, files in os.walk(self.output_dir):
            for file in files:
                full_path = os.path.join(root, file)
                local_files.append(full_path)

        total_local = len(local_files)
        expected_local_count = self.downloaded_files + self.skipped_files

        print(f"远程文件总数: {total_expected}")
        print(f"本地文件总数: {total_local}")
        print(f"成功下载: {self.downloaded_files}")
        print(f"跳过（已存在）: {self.skipped_files}")
        print(f"失败: {self.failed_files}")
        print(f"预期本地应有: {expected_local_count}")

        if total_local == expected_local_count and self.failed_files == 0:
            print("\n✓ 文件完整性校验通过！所有文件下载完整。")
            return True
        else:
            print("\n✗ 文件完整性校验未通过！")

            missing_files = []
            for expected_file in self.expected_files:
                if not os.path.exists(expected_file):
                    missing_files.append(expected_file)

            if missing_files:
                print(f"\n缺失文件列表（共 {len(missing_files)} 个）:")
                for i, missing in enumerate(missing_files[:20], 1):
                    print(f"  {i}. {os.path.basename(missing)}")
                if len(missing_files) > 20:
                    print(f"  ... 还有 {len(missing_files) - 20} 个文件未显示")

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

        download_threads = self.start_download_workers()

        print("\n扫描目录结构中...")
        try:
            self.process_directory(self.base_url)
        except Exception as e:
            print(f"扫描过程出错: {str(e)}")

        print(f"\n等待下载完成，文件数量: {self.file_queue.qsize()}...")
        self.file_queue.join()

        for _ in range(self.max_workers):
            self.file_queue.put((None, None))

        print("正在关闭下载线程...")
        for t in download_threads:
            t.join(timeout=2.0)

        print("-" * 50)
        print(f"下载完成!")
        print(f"成功: {self.downloaded_files} 个文件")
        print(f"跳过: {self.skipped_files} 个文件（已存在）")
        print(f"失败: {self.failed_files} 个文件")

        self.verify_downloads()


def main():
    parser = argparse.ArgumentParser(
        description='递归下载镜像站点文件，支持查漏补缺',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''使用示例:
  # 默认下载阿里云Alpine镜像（x86_64架构，main+community）
  python download.py

  # 下载指定URL
  python download.py -u https://mirrors.aliyun.com/alpine/v3.22/

  # 指定CPU架构
  python download.py -u https://mirrors.aliyun.com/alpine/v3.23/ -a aarch64

  # 设置下载延迟（避免请求过快）
  python download.py -u https://example.com/ -d 1.0

  # 设置并发线程数（默认50）
  python download.py -u https://example.com/ -w 100

  # 下载完整镜像（所有架构）
  python download.py -u https://mirrors.aliyun.com/alpine/v3.23/ -a all

  # 仅检查包完整性（查漏）
  python download.py --check-only

  # 查漏补缺（同步模式）
  python download.py --sync

  # 指定输出目录
  python download.py -u https://example.com/repo/ -o ./my-downloads

注意: 强制保留完整的远程目录层级结构（包括主机名）
      下载时会自动跳过已存在的文件
'''
    )

    parser.add_argument(
        '-a', '--arch',
        default='x86_64',
        help='指定CPU架构 (默认: x86_64)'
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

    parser.add_argument(
        '--check-only',
        action='store_true',
        help='仅检查包完整性，不下载'
    )

    parser.add_argument(
        '--sync',
        action='store_true',
        help='同步模式：查漏补缺，仅下载缺失的包'
    )

    args = parser.parse_args()

    base_url = args.url.rstrip('/')

    if os.path.isabs(args.output):
        output_dir = args.output
    else:
        output_dir = os.path.join(os.getcwd(), args.output)

    os.makedirs(output_dir, exist_ok=True)

    if 'mirrors.aliyun.com/alpine/v' in base_url and args.arch:
        host = urlparse(base_url).netloc
        base_output_dir = os.path.join(output_dir, host, 'alpine', 'v3.23')

        if args.check_only or args.sync:
            print("=" * 60)
            print("检查本地与远程仓库的包差异...")
            print("=" * 60)

            remote_info = get_remote_package_list(base_url, args.arch)

            print(f"\n远程仓库 (Alpine v3.23, {args.arch}):")
            print(f"  main:      {remote_info['main_total']} 个包")
            print(f"  community: {remote_info['community_total']} 个包")
            print(f"  总计:      {remote_info['main_total'] + remote_info['community_total']} 个包")

            local_pkgs = get_local_packages(output_dir, base_url, args.arch)

            result = compare_and_report(local_pkgs, remote_info, base_url, args.arch)

            print(f"\n本地仓库:")
            print(f"  main:      {result['local_main']} 个包")
            print(f"  community: {result['local_community']} 个包")
            print(f"  总计:      {len(local_pkgs)} 个包")

            print(f"\n差异分析:")
            print(f"  main 仓库缺失:      {result['missing_main_count']} 个")
            print(f"  community 仓库缺失: {result['missing_community_count']} 个")
            print(f"  总缺失:             {result['missing_main_count'] + result['missing_community_count']} 个")

            if result['missing_main_count'] > 0:
                print(f"\nmain 仓库缺失包（前20个）:")
                for pkg in sorted(result['missing_main'])[:20]:
                    print(f"  {pkg}")
            if result['missing_community_count'] > 0:
                print(f"\ncommunity 仓库缺失包（前20个）:")
                for pkg in sorted(result['missing_community'])[:20]:
                    print(f"  {pkg}")

            if args.sync and (result['missing_main_count'] + result['missing_community_count']) > 0:
                print("\n" + "=" * 60)
                print("开始查漏补缺...")
                print("=" * 60)

                all_missing = list(result['missing_main']) + list(result['missing_community'])

                if result['missing_main_count'] > 0:
                    print(f"\n>>> 补充 main 仓库缺失包...")
                    main_success, main_failed = download_missing_packages(
                        [(p, p.split('/')[-1]) for p in result['missing_main']],
                        base_url, base_output_dir, args.workers, args.timeout
                    )
                    print(f"main 仓库: 成功 {main_success}, 失败 {main_failed}")

                if result['missing_community_count'] > 0:
                    print(f"\n>>> 补充 community 仓库缺失包...")
                    comm_success, comm_failed = download_missing_packages(
                        [(p, p.split('/')[-1]) for p in result['missing_community']],
                        base_url, base_output_dir, args.workers, args.timeout
                    )
                    print(f"community 仓库: 成功 {comm_success}, 失败 {comm_failed}")

                print("\n" + "=" * 60)
                print("查漏补缺完成!")
                print("=" * 60)

            return

        if args.arch == 'all':
            print(f"将下载所有架构...")
            print("-" * 50)

            arch_urls = []
            for repo in ['main', 'community']:
                repo_url = f"{base_url}/{repo}/"
                try:
                    response = requests.get(repo_url, timeout=30)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for a_tag in soup.find_all('a', href=True):
                        href = a_tag.get('href')
                        if href and isinstance(href, str) and href.endswith('/') and not href.startswith('.'):
                            arch = href.rstrip('/')
                            if arch in ['x86_64', 'aarch64', 'armhf', 'armv7', 'loongarch64', 'ppc64le', 'riscv64', 's390x', 'x86']:
                                arch_urls.append((repo, arch, f"{base_url}/{repo}/{arch}/"))
                except Exception as e:
                    print(f"获取架构列表失败: {e}")

            total_downloaded = 0
            total_skipped = 0
            total_failed = 0

            for repo, arch, url in arch_urls:
                print(f"\n>>> 下载 {repo}/{arch} ...")
                downloader = RecursiveDownloader(
                    base_url=url,
                    output_dir=output_dir,
                    delay=args.delay,
                    timeout=args.timeout,
                    max_workers=args.workers
                )
                downloader.run()
                total_downloaded += downloader.downloaded_files
                total_skipped += downloader.skipped_files
                total_failed += downloader.failed_files

            print("\n" + "=" * 50)
            print(f"全部下载完成!")
            print(f"总计成功: {total_downloaded} 个文件")
            print(f"总计跳过: {total_skipped} 个文件")
            print(f"总计失败: {total_failed} 个文件")
            return
        else:
            main_url = f"{base_url}/main/{args.arch}/"
            community_url = f"{base_url}/community/{args.arch}/"
            print(f"架构参数: {args.arch}")
            print(f"将下载以下URL:")
            print(f"  - {main_url}")
            print(f"  - {community_url}")
            print("-" * 50)

            print(f"输出目录(绝对路径): {output_dir}")

            os.makedirs(output_dir, exist_ok=True)

            print(f"\n>>> 下载 main 仓库...")
            downloader_main = RecursiveDownloader(
                base_url=main_url,
                output_dir=output_dir,
                delay=args.delay,
                timeout=args.timeout,
                max_workers=args.workers
            )
            downloader_main.run()

            print(f"\n>>> 下载 community 仓库...")
            downloader_community = RecursiveDownloader(
                base_url=community_url,
                output_dir=output_dir,
                delay=args.delay,
                timeout=args.timeout,
                max_workers=args.workers
            )
            downloader_community.run()

            print("\n" + "=" * 50)
            print(f"全部下载完成!")
            print(f"总计成功: {downloader_main.downloaded_files + downloader_community.downloaded_files} 个文件")
            print(f"总计跳过: {downloader_main.skipped_files + downloader_community.skipped_files} 个文件")
            print(f"总计失败: {downloader_main.failed_files + downloader_community.failed_files} 个文件")
            return

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