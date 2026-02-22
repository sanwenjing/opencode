# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import subprocess
import argparse
import re

PATH_SEP = os.sep


def get_output_path(filename: str) -> str:
    return os.path.join(os.getcwd(), filename)


def check_nmap():
    """检查nmap是否已安装"""
    try:
        subprocess.run(['nmap', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def run_nmap(args_list):
    """执行nmap命令"""
    cmd = ['nmap'] + args_list
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout + result.stderr
        return output, "", result.returncode
    except FileNotFoundError:
        return "", "错误: nmap未安装，请先安装nmap", 1


def cmd_scan(target, ports=None, output=None, verbose=False, timing=3):
    """基本端口扫描"""
    args = []
    if verbose:
        args.append('-v')
    args.extend([f'-T{timing}', target])
    
    if ports:
        args.extend(['-p', ports])
    
    stdout, stderr, code = run_nmap(args)
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, stderr, code


def cmd_quick(target, output=None, verbose=False):
    """快速扫描（100个常用端口）"""
    args = ['-F']
    if verbose:
        args.append('-v')
    args.append(target)
    
    stdout, stderr, code = run_nmap(args)
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, stderr, code


def cmd_discover(target, output=None, verbose=False):
    """主机发现（ARP扫描）"""
    args = ['-sn']
    
    is_local = target.startswith('192.168.') or target.startswith('10.') or target.startswith('172.')
    if is_local:
        args.append('-PR')
    
    if verbose:
        args.append('-vv')
    args.append(target)
    
    stdout, stderr, code = run_nmap(args)
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, stderr, code


def cmd_service(target, ports=None, output=None, verbose=False):
    """服务版本检测"""
    args = ['-sV']
    if verbose:
        args.append('-v')
    
    if ports:
        args.extend(['-p', ports])
    
    args.append(target)
    
    stdout, stderr, code = run_nmap(args)
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, stderr, code


def cmd_os(target, output=None, verbose=False):
    """操作系统检测"""
    args = ['-O']
    if verbose:
        args.append('-v')
    args.append(target)
    
    stdout, stderr, code = run_nmap(args)
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, stderr, code


def cmd_full(target, output=None, verbose=False):
    """完整扫描（服务版本+操作系统+脚本）"""
    args = ['-A']
    if verbose:
        args.append('-v')
    args.append(target)
    
    stdout, stderr, code = run_nmap(args)
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, stderr, code


def main():
    parser = argparse.ArgumentParser(
        description='Nmap网络扫描工具封装',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  %(prog)s scan 192.168.1.1
  %(prog)s scan 192.168.1.1 -p 80,443
  %(prog)s quick 192.168.1.1
  %(prog)s discover 192.168.1.0/24
  %(prog)s service 192.168.1.1
  %(prog)s os 192.168.1.1
  %(prog)s full 192.168.1.1 -o result.txt
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # scan命令
    parser_scan = subparsers.add_parser('scan', help='基本端口扫描')
    parser_scan.add_argument('target', help='目标IP或域名')
    parser_scan.add_argument('-p', '--ports', help='指定端口（如: 80,443 或 1-1000）')
    parser_scan.add_argument('-o', '--output', help='保存结果到文件')
    parser_scan.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    parser_scan.add_argument('-t', '--timing', type=int, default=3, choices=range(0,6), help='扫描速度(0-5)')
    
    # quick命令
    parser_quick = subparsers.add_parser('quick', help='快速扫描（100个常用端口）')
    parser_quick.add_argument('target', help='目标IP或域名')
    parser_quick.add_argument('-o', '--output', help='保存结果到文件')
    parser_quick.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    # discover命令
    parser_discover = subparsers.add_parser('discover', help='主机发现')
    parser_discover.add_argument('target', help='目标网络（如: 192.168.1.0/24）')
    parser_discover.add_argument('-o', '--output', help='保存结果到文件')
    parser_discover.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    # service命令
    parser_service = subparsers.add_parser('service', help='服务版本检测')
    parser_service.add_argument('target', help='目标IP或域名')
    parser_service.add_argument('-p', '--ports', help='指定端口')
    parser_service.add_argument('-o', '--output', help='保存结果到文件')
    parser_service.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    # os命令
    parser_os = subparsers.add_parser('os', help='操作系统检测')
    parser_os.add_argument('target', help='目标IP或域名')
    parser_os.add_argument('-o', '--output', help='保存结果到文件')
    parser_os.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    # full命令
    parser_full = subparsers.add_parser('full', help='完整扫描（服务版本+操作系统+脚本）')
    parser_full.add_argument('target', help='目标IP或域名')
    parser_full.add_argument('-o', '--output', help='保存结果到文件')
    parser_full.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if not check_nmap():
        print("错误: nmap未安装")
        print("请先安装nmap:")
        print("  Ubuntu/Debian: sudo apt install nmap")
        print("  CentOS/RHEL: sudo yum install nmap")
        print("  macOS: brew install nmap")
        return
    
    target = getattr(args, 'target', None)
    output = getattr(args, 'output', None)
    verbose = getattr(args, 'verbose', False)
    
    commands = {
        'scan': lambda: cmd_scan(target, args.ports, output, verbose, args.timing),
        'quick': lambda: cmd_quick(target, output, verbose),
        'discover': lambda: cmd_discover(target, output, verbose),
        'service': lambda: cmd_service(target, args.ports, output, verbose),
        'os': lambda: cmd_os(target, output, verbose),
        'full': lambda: cmd_full(target, output, verbose),
    }
    
    if args.command in commands:
        stdout, stderr, code = commands[args.command]()
        if stdout:
            print(stdout)
        if stderr and code != 0:
            print(stderr, file=sys.stderr)


if __name__ == '__main__':
    main()
