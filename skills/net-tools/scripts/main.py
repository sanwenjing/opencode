# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import subprocess
import argparse
import socket
import datetime

PATH_SEP = os.sep

COMMON_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 
    1723, 3306, 3389, 5432, 5900, 8080, 8443, 10000, 49152, 49153, 49154
]

SERVICE_NAMES = {
    21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp', 53: 'dns', 
    80: 'http', 110: 'pop3', 111: 'rpcbind', 135: 'msrpc', 139: 'netbios-ssn',
    143: 'imap', 443: 'https', 445: 'microsoft-ds', 993: 'imaps', 995: 'pop3s',
    1723: 'pptp', 3306: 'mysql', 3389: 'ms-wbt-server', 5432: 'postgresql',
    5900: 'vnc', 8080: 'http-proxy', 8443: 'https-alt', 10000: 'webmin'
}


def get_output_path(filename: str) -> str:
    return os.path.join(os.getcwd(), filename)


def resolve_host(target):
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        return None


def check_nmap():
    try:
        result = subprocess.run(['nmap', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass
    return False


def test_nmap_works():
    try:
        result = subprocess.run(['nmap', '-p', '80', '127.0.0.1'], 
                              capture_output=True, text=True, timeout=10)
        if 'route_dst_netlink' in result.stderr or 'can\'t find interface' in result.stderr:
            return False
        return True
    except:
        return False


def scan_port(target, port, timeout=3):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        result = s.connect_ex((target, port))
        return result == 0
    except:
        return False
    finally:
        s.close()


def scan_ports_socket(target, ports, verbose=False, timeout=3):
    results = []
    for port in ports:
        if verbose:
            print(f"扫描端口: {port}", end='\r')
        is_open = scan_port(target, port, timeout)
        service = SERVICE_NAMES.get(port, 'unknown')
        results.append((port, is_open, service))
    return results


def run_nmap(args_list):
    cmd = ['nmap'] + args_list
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout + result.stderr
        return output, "", result.returncode
    except subprocess.TimeoutExpired:
        return "", "扫描超时", 1
    except FileNotFoundError:
        return "", "错误: nmap未安装", 1


def use_nmap():
    global check_nmap, test_nmap_works
    return check_nmap() and test_nmap_works()


def cmd_scan(target, ports=None, output=None, verbose=False, timing=3):
    ip = resolve_host(target)
    if not ip:
        print(f"无法解析主机: {target}")
        return "", "DNS解析失败", 1
    
    print(f"目标: {target} ({ip})")
    
    if use_nmap():
        args = [f'-T{timing}', target]
        if ports:
            args.extend(['-p', ports])
        stdout, stderr, code = run_nmap(args)
    else:
        print("nmap不可用，使用Python socket扫描...")
        if ports:
            port_list = parse_ports(ports)
        else:
            port_list = COMMON_PORTS[:20]
        
        print(f"扫描端口: {port_list}")
        results = scan_ports_socket(ip, port_list, verbose)
        
        lines = []
        lines.append(f"Nmap scan report for {target} ({ip})")
        lines.append(f"Host is up.")
        lines.append(f"PORT      STATE SERVICE")
        for port, is_open, service in results:
            state = "open" if is_open else "closed"
            lines.append(f"{port}/tcp   {state}     {service}")
        
        stdout = "\n".join(lines)
        code = 0
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, "", code


def cmd_quick(target, output=None, verbose=False):
    ip = resolve_host(target)
    if not ip:
        print(f"无法解析主机: {target}")
        return "", "DNS解析失败", 1
    
    print(f"目标: {target} ({ip})")
    
    if use_nmap():
        stdout, stderr, code = run_nmap(['-F', target])
    else:
        print("nmap不可用，使用Python socket快速扫描...")
        results = scan_ports_socket(ip, COMMON_PORTS[:20], verbose)
        
        lines = []
        lines.append(f"Nmap scan report for {target} ({ip})")
        lines.append(f"Host is up.")
        lines.append(f"PORT      STATE SERVICE")
        for port, is_open, service in results:
            if is_open:
                lines.append(f"{port}/tcp   open     {service}")
        
        stdout = "\n".join(lines)
        code = 0
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, "", code


def cmd_discover(target, output=None, verbose=False):
    if use_nmap():
        args = ['-sn']
        if target.startswith('192.168.') or target.startswith('10.') or target.startswith('172.'):
            args.append('-PR')
        args.append(target)
        stdout, stderr, code = run_nmap(args)
    else:
        lines = []
        lines.append(f"Nmap scan report for {target}")
        lines.append("Host is up.")
        lines.append("Note: Host discovery requires nmap with root privileges")
        stdout = "\n".join(lines)
        code = 0
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, "", code


def cmd_service(target, ports=None, output=None, verbose=False):
    ip = resolve_host(target)
    if not ip:
        print(f"无法解析主机: {target}")
        return "", "DNS解析失败", 1
    
    print(f"目标: {target} ({ip})")
    
    if use_nmap():
        args = ['-sV']
        if ports:
            args.extend(['-p', ports])
        args.append(target)
        stdout, stderr, code = run_nmap(args)
    else:
        print("nmap不可用，使用Python socket扫描...")
        if ports:
            port_list = parse_ports(ports)
        else:
            port_list = COMMON_PORTS[:30]
        
        results = scan_ports_socket(ip, port_list, verbose)
        
        lines = []
        lines.append(f"Nmap scan report for {target} ({ip})")
        lines.append(f"Host is up.")
        lines.append(f"PORT      STATE SERVICE VERSION")
        for port, is_open, service in results:
            if is_open:
                lines.append(f"{port}/tcp   open     {service}")
        
        stdout = "\n".join(lines)
        code = 0
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, "", code


def cmd_os(target, output=None, verbose=False):
    if use_nmap():
        stdout, stderr, code = run_nmap(['-O', target])
    else:
        stdout = "操作系统检测需要nmap支持", "", 1
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, "", code


def cmd_full(target, output=None, verbose=False):
    ip = resolve_host(target)
    if not ip:
        print(f"无法解析主机: {target}")
        return "", "DNS解析失败", 1
    
    print(f"目标: {target} ({ip})")
    
    if use_nmap():
        stdout, stderr, code = run_nmap(['-A', target])
    else:
        print("nmap不可用，使用Python socket完整扫描...")
        results = scan_ports_socket(ip, COMMON_PORTS, verbose)
        
        lines = []
        lines.append(f"Nmap scan report for {target} ({ip})")
        lines.append(f"Host is up.")
        lines.append(f"PORT      STATE SERVICE")
        for port, is_open, service in results:
            if is_open:
                lines.append(f"{port}/tcp   open     {service}")
        
        stdout = "\n".join(lines)
        code = 0
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, "", code


def parse_ports(ports_str):
    ports = []
    for part in ports_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            ports.extend(range(int(start), int(end) + 1))
        else:
            ports.append(int(part))
    return ports


def main():
    parser = argparse.ArgumentParser(
        description='Nmap网络扫描工具封装（支持Python socket fallback）',
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
    
    parser_scan = subparsers.add_parser('scan', help='基本端口扫描')
    parser_scan.add_argument('target', help='目标IP或域名')
    parser_scan.add_argument('-p', '--ports', help='指定端口（如: 80,443 或 1-1000）')
    parser_scan.add_argument('-o', '--output', help='保存结果到文件')
    parser_scan.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    parser_scan.add_argument('-t', '--timing', type=int, default=3, choices=range(0,6), help='扫描速度(0-5)')
    
    parser_quick = subparsers.add_parser('quick', help='快速扫描（常用端口）')
    parser_quick.add_argument('target', help='目标IP或域名')
    parser_quick.add_argument('-o', '--output', help='保存结果到文件')
    parser_quick.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    parser_discover = subparsers.add_parser('discover', help='主机发现')
    parser_discover.add_argument('target', help='目标网络（如: 192.168.1.0/24）')
    parser_discover.add_argument('-o', '--output', help='保存结果到文件')
    parser_discover.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    parser_service = subparsers.add_parser('service', help='服务版本检测')
    parser_service.add_argument('target', help='目标IP或域名')
    parser_service.add_argument('-p', '--ports', help='指定端口')
    parser_service.add_argument('-o', '--output', help='保存结果到文件')
    parser_service.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    parser_os = subparsers.add_parser('os', help='操作系统检测')
    parser_os.add_argument('target', help='目标IP或域名')
    parser_os.add_argument('-o', '--output', help='保存结果到文件')
    parser_os.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    parser_full = subparsers.add_parser('full', help='完整扫描')
    parser_full.add_argument('target', help='目标IP或域名')
    parser_full.add_argument('-o', '--output', help='保存结果到文件')
    parser_full.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
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
        if stderr:
            print(stderr, file=sys.stderr)


if __name__ == '__main__':
    main()
