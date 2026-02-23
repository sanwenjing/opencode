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
import json
import re

PATH_SEP = os.sep


def get_output_path(filename: str) -> str:
    return os.path.join(os.getcwd(), filename)


def resolve_host(target):
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        return None


def run_cmd(cmd, timeout=30):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True)
        return result.stdout + result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "命令执行超时", 1
    except FileNotFoundError:
        return f"命令未找到: {cmd.split()[0]}", 1


def check_tool(name):
    paths = ['/usr/bin/' + name, '/bin/' + name, '/usr/sbin/' + name, '/sbin/' + name]
    for p in paths:
        if os.path.exists(p):
            return True
    try:
        subprocess.run([name, '--version'], capture_output=True, timeout=5)
        return True
    except:
        return False


def check_nmap():
    try:
        result = subprocess.run(['nmap', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass
    return False


def install_nmap():
    import platform
    system = platform.system().lower()
    
    print("nmap未安装，正在尝试自动安装...")
    
    commands = {
        'linux': {
            'debian': ['sudo', 'apt', 'install', '-y', 'nmap'],
            'ubuntu': ['sudo', 'apt', 'install', '-y', 'nmap'],
            'centos': ['sudo', 'yum', 'install', '-y', 'nmap'],
            'fedora': ['sudo', 'dnf', 'install', '-y', 'nmap'],
            'arch': ['sudo', 'pacman', '-S', '--noconfirm', 'nmap'],
            'alpine': ['sudo', 'apk', 'add', 'nmap'],
            'termux': ['pkg', 'install', 'nmap'],
        },
        'darwin': ['brew', 'install', 'nmap'],
        'windows': ['choco', 'install', 'nmap'],
    }
    
    if system == 'linux':
        import subprocess
        result = subprocess.run(['cat', '/etc/os-release'], capture_output=True, text=True)
        os_info = result.stdout.lower()
        
        for name, cmd in commands['linux'].items():
            if name in os_info:
                print(f"检测到 {name}，执行: {' '.join(cmd)}")
                try:
                    subprocess.run(cmd, timeout=120)
                    if check_nmap():
                        print("nmap安装成功!")
                        return True
                except Exception as e:
                    print(f"安装失败: {e}")
                    break
    
    elif system == 'darwin':
        try:
            print(f"执行: {' '.join(commands['darwin'])}")
            subprocess.run(commands['darwin'], timeout=120)
            if check_nmap():
                print("nmap安装成功!")
                return True
        except Exception as e:
            print(f"安装失败: {e}")
    
    print("\n自动安装失败，请手动安装:")
    print("  Ubuntu/Debian: sudo apt install nmap")
    print("  CentOS/RHEL: sudo yum install nmap")
    print("  macOS: brew install nmap")
    print("  Termux: pkg install nmap")
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


def run_nmap(args_list):
    cmd = ['nmap'] + args_list
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout + result.stderr
        return output, result.returncode
    except subprocess.TimeoutExpired:
        return "扫描超时", 1
    except FileNotFoundError:
        return "错误: nmap未安装", 1


def use_nmap():
    if not check_nmap():
        return install_nmap() and test_nmap_works()
    if test_nmap_works():
        return True
    print("错误: nmap已安装但无法正常工作（网络权限限制）")
    print("请确保nmap有网络访问权限")
    return False


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


def cmd_scan(target, ports=None, output=None, verbose=False, timing=3, service=False, os_detect=False):
    if not use_nmap():
        print("错误: nmap不可用，请先安装nmap")
        sys.exit(1)
    
    ip = resolve_host(target)
    if not ip:
        print(f"无法解析主机: {target}")
        return "DNS解析失败", 1
    
    print(f"目标: {target} ({ip})")
    
    args = [f'-T{timing}']
    
    if ports:
        args.extend(['-p', ports])
    else:
        args.append('-p-')
    
    if service:
        args.append('-sV')
    if os_detect:
        args.append('-O')
    
    if verbose:
        args.append('-v')
    
    args.append(target)
    
    stdout, code = run_nmap(args)
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, code


def cmd_ping(target, count=4, output=None):
    print(f"Ping {target}...")
    stdout, code = run_cmd(f"ping -c {count} {target}")
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, code


def cmd_traceroute(target, output=None):
    print(f"Traceroute to {target}...")
    stdout, code = run_cmd(f"traceroute {target}")
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, code


def cmd_mtr(target, count=10, output=None):
    print(f"MTR to {target}...")
    stdout, code = run_cmd(f"mtr -c {count} {target}")
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, code


def cmd_curl(url, method='GET', data=None, headers=None, output=None, follow=True):
    cmd = f"curl -s"
    if not follow:
        cmd += " -L"
    cmd += f" -X {method}"
    if headers:
        for k, v in headers.items():
            cmd += f" -H '{k}: {v}'"
    if data:
        cmd += f" -d '{data}'"
    cmd += f" '{url}'"
    
    print(f"{method} {url}")
    stdout, code = run_cmd(cmd, timeout=30)
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, code


def cmd_wget(url, output=None, mirror=False):
    if output:
        cmd = f"wget -O {output} '{url}'"
    elif mirror:
        cmd = f"wget -mk '{url}'"
    else:
        cmd = f"wget '{url}'"
    
    print(f"Downloading {url}...")
    stdout, code = run_cmd(cmd, timeout=60)
    
    if output and code == 0:
        print(f"文件已保存到: {output}")
    
    return stdout, code


def cmd_netcat(target, port, mode='connect', output=None):
    if mode == 'connect':
        print(f"连接 {target}:{port}...")
        cmd = f"nc -zv {target} {port}"
        stdout, code = run_cmd(cmd)
    elif mode == 'listen':
        print(f"监听端口 {port}...")
        cmd = f"nc -l -p {port}"
        stdout, code = run_cmd(cmd, timeout=10)
    else:
        return "无效模式", 1
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
    
    return stdout, code


def cmd_ss(args=None, output=None):
    print("查看套接字统计...")
    cmd = "ss"
    if args:
        for arg in args:
            if not arg.startswith('-'):
                arg = '-' + arg
            cmd += " " + arg
    stdout, code = run_cmd(cmd)
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, code


def cmd_netstat(args=None, output=None):
    print("查看网络统计...")
    cmd = "netstat"
    if args:
        cmd += " " + " ".join(args)
    stdout, code = run_cmd(cmd)
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, code


def cmd_dig(domain, record_type='A', dns_server=None, output=None):
    print(f"DNS查询: {domain} ({record_type})...")
    cmd = f"dig {domain} {record_type}"
    if dns_server:
        cmd += f" @{dns_server}"
    stdout, code = run_cmd(cmd)
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, code


def cmd_nslookup(domain, dns_server=None, output=None):
    print(f"NSLookup: {domain}...")
    cmd = f"nslookup {domain}"
    if dns_server:
        cmd += f" {dns_server}"
    stdout, code = run_cmd(cmd)
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, code


def cmd_host(domain, output=None):
    print(f"Host查询: {domain}...")
    stdout, code = run_cmd(f"host {domain}")
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, code


def cmd_whois(domain, output=None):
    print(f"Whois查询: {domain}...")
    stdout, code = run_cmd(f"whois {domain}")
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, code


def cmd_tcpdump(interface=None, count=10, host=None, port=None, output=None):
    print("Tcpdump抓包...")
    cmd = f"tcpdump -c {count}"
    if interface:
        cmd += f" -i {interface}"
    if host:
        cmd += f" host {host}"
    if port:
        cmd += f" port {port}"
    cmd += " -n"
    
    stdout, code = run_cmd(cmd, timeout=30)
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, code


def cmd_ngrep(pattern, interface=None, host=None, port=None, output=None):
    print(f"Ngrep: {pattern}...")
    cmd = f"ngrep -d any"
    if interface:
        cmd = f"ngrep -i {interface}"
    if host:
        cmd += f" host {host}"
    if port:
        cmd += f" port {port}"
    cmd += f" '{pattern}'"
    
    stdout, code = run_cmd(cmd, timeout=20)
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, code


def cmd_iperf(server, client=None, port=5201, time_sec=10, output=None):
    if client:
        print(f"Iperf3 客户端测试 -> {server}")
        cmd = f"iperf3 -c {server} -p {port} -t {time_sec}"
    else:
        print(f"Iperf3 服务器模式，监听端口 {port}")
        cmd = f"iperf3 -s -p {port}"
    
    stdout, code = run_cmd(cmd, timeout=time_sec + 10)
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, code


def cmd_ip_addr(output=None):
    print("查看IP配置...")
    stdout, code = run_cmd("ip addr")
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, code


def cmd_ip_route(output=None):
    print("查看路由表...")
    stdout, code = run_cmd("ip route")
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, code


def cmd_ifconfig(interface=None, output=None):
    print("查看网络接口...")
    cmd = "ifconfig" if interface else f"ifconfig {interface}"
    stdout, code = run_cmd(cmd)
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, code


def cmd_route_table(output=None):
    print("查看路由表...")
    stdout, code = run_cmd("route -n")
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, code


def cmd_arp(output=None):
    print("查看ARP缓存...")
    stdout, code = run_cmd("arp -a")
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, code


def cmd_telnet(host, port, output=None):
    print(f"Telnet {host}:{port}...")
    cmd = f"echo '' | telnet {host} {port}"
    stdout, code = run_cmd(cmd, timeout=10)
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, code


def cmd_ftp(host, user='anonymous', password='anonymous@', output=None):
    print(f"FTP连接 {host}...")
    cmd = f"echo -e 'user {user} {password}\\nls\\nquit' | ftp {host}"
    stdout, code = run_cmd(cmd, timeout=30)
    
    if output:
        output_path = get_output_path(output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(stdout)
        print(f"结果已保存到: {output_path}")
    
    return stdout, code


def main():
    parser = argparse.ArgumentParser(
        description='网络工具箱 - 集成多种网络工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    parser_scan = subparsers.add_parser('scan', help='端口扫描（默认全端口）')
    parser_scan.add_argument('target', help='目标IP或域名')
    parser_scan.add_argument('-p', '--ports', help='指定端口（如: 80,443 或 1-1000）')
    parser_scan.add_argument('-o', '--output', help='保存结果到文件')
    parser_scan.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    parser_scan.add_argument('-t', '--timing', type=int, default=3, choices=range(0,6), help='扫描速度(0-5)')
    parser_scan.add_argument('-s', '--service', action='store_true', help='检测服务版本')
    parser_scan.add_argument('-O', '--os', action='store_true', help='检测操作系统')
    
    parser_ping = subparsers.add_parser('ping', help='Ping测试')
    parser_ping.add_argument('target', help='目标IP或域名')
    parser_ping.add_argument('-c', '--count', type=int, default=4, help='ping次数')
    parser_ping.add_argument('-o', '--output', help='保存结果')
    
    parser_traceroute = subparsers.add_parser('traceroute', help='路由追踪')
    parser_traceroute.add_argument('target', help='目标')
    parser_traceroute.add_argument('-o', '--output', help='保存结果')
    
    parser_mtr = subparsers.add_parser('mtr', help='MTR诊断')
    parser_mtr.add_argument('target', help='目标')
    parser_mtr.add_argument('-c', '--count', type=int, default=10)
    parser_mtr.add_argument('-o', '--output', help='保存结果')
    
    parser_curl = subparsers.add_parser('curl', help='HTTP请求')
    parser_curl.add_argument('url', help='URL')
    parser_curl.add_argument('-X', '--method', default='GET', help='HTTP方法')
    parser_curl.add_argument('-d', '--data', help='请求数据')
    parser_curl.add_argument('-H', '--header', action='append', help='HTTP头')
    parser_curl.add_argument('-o', '--output', help='保存结果')
    parser_curl.add_argument('--no-follow', action='store_true', help='不跟随重定向')
    
    parser_wget = subparsers.add_parser('wget', help='文件下载')
    parser_wget.add_argument('url', help='URL')
    parser_wget.add_argument('-o', '--output', help='保存文件名')
    parser_wget.add_argument('-m', '--mirror', action='store_true', help='镜像下载')
    
    parser_nc = subparsers.add_parser('nc', help='NetCat连接')
    parser_nc.add_argument('target', help='目标IP')
    parser_nc.add_argument('port', type=int, help='端口')
    parser_nc.add_argument('-m', '--mode', default='connect', choices=['connect', 'listen'], help='模式')
    parser_nc.add_argument('-o', '--output', help='保存结果')
    
    parser_ss = subparsers.add_parser('ss', help='套接字统计')
    parser_ss.add_argument('args', nargs='*', help='ss参数')
    parser_ss.add_argument('-o', '--output', help='保存结果')
    
    parser_netstat = subparsers.add_parser('netstat', help='网络统计')
    parser_netstat.add_argument('args', nargs='*', help='netstat参数')
    parser_netstat.add_argument('-o', '--output', help='保存结果')
    
    parser_dig = subparsers.add_parser('dig', help='DNS查询')
    parser_dig.add_argument('domain', help='域名')
    parser_dig.add_argument('record_type', nargs='?', default='A', help='记录类型')
    parser_dig.add_argument('-s', '--server', help='DNS服务器')
    parser_dig.add_argument('-o', '--output', help='保存结果')
    
    parser_nslookup = subparsers.add_parser('nslookup', help='DNS查询')
    parser_nslookup.add_argument('domain', help='域名')
    parser_nslookup.add_argument('-s', '--server', help='DNS服务器')
    parser_nslookup.add_argument('-o', '--output', help='保存结果')
    
    parser_host = subparsers.add_parser('host', help='DNS查询')
    parser_host.add_argument('domain', help='域名')
    parser_host.add_argument('-o', '--output', help='保存结果')
    
    parser_whois = subparsers.add_parser('whois', help='Whois查询')
    parser_whois.add_argument('domain', help='域名')
    parser_whois.add_argument('-o', '--output', help='保存结果')
    
    parser_tcpdump = subparsers.add_parser('tcpdump', help='抓包')
    parser_tcpdump.add_argument('-c', '--count', type=int, default=10, help='包数量')
    parser_tcpdump.add_argument('-i', '--interface', help='接口')
    parser_tcpdump.add_argument('--host', help='主机')
    parser_tcpdump.add_argument('-p', '--port', type=int, help='端口')
    parser_tcpdump.add_argument('-o', '--output', help='保存结果')
    
    parser_ngrep = subparsers.add_parser('ngrep', help='网络包搜索')
    parser_ngrep.add_argument('pattern', help='匹配模式')
    parser_ngrep.add_argument('-i', '--interface', help='接口')
    parser_ngrep.add_argument('--host', help='主机')
    parser_ngrep.add_argument('-p', '--port', type=int, help='端口')
    parser_ngrep.add_argument('-o', '--output', help='保存结果')
    
    parser_iperf = subparsers.add_parser('iperf3', help='带宽测试')
    parser_iperf.add_argument('target', nargs='?', help='服务器地址')
    parser_iperf.add_argument('-c', '--client', action='store_true', help='客户端模式')
    parser_iperf.add_argument('-p', '--port', type=int, default=5201, help='端口')
    parser_iperf.add_argument('-t', '--time', type=int, default=10, help='测试时间')
    parser_iperf.add_argument('-o', '--output', help='保存结果')
    
    parser_ip_addr = subparsers.add_parser('ip-addr', help='IP配置')
    parser_ip_addr.add_argument('-o', '--output', help='保存结果')
    
    parser_ip_route = subparsers.add_parser('ip-route', help='路由表')
    parser_ip_route.add_argument('-o', '--output', help='保存结果')
    
    parser_ifconfig = subparsers.add_parser('ifconfig', help='网络接口')
    parser_ifconfig.add_argument('interface', nargs='?', help='接口名')
    parser_ifconfig.add_argument('-o', '--output', help='保存结果')
    
    parser_route = subparsers.add_parser('route', help='路由表')
    parser_route.add_argument('-o', '--output', help='保存结果')
    
    parser_arp = subparsers.add_parser('arp', help='ARP缓存')
    parser_arp.add_argument('-o', '--output', help='保存结果')
    
    parser_telnet = subparsers.add_parser('telnet', help='Telnet测试')
    parser_telnet.add_argument('host', help='主机')
    parser_telnet.add_argument('port', type=int, help='端口')
    parser_telnet.add_argument('-o', '--output', help='保存结果')
    
    parser_ftp = subparsers.add_parser('ftp', help='FTP连接')
    parser_ftp.add_argument('host', help='FTP服务器')
    parser_ftp.add_argument('-u', '--user', default='anonymous', help='用户名')
    parser_ftp.add_argument('-p', '--password', default='anonymous@', help='密码')
    parser_ftp.add_argument('-o', '--output', help='保存结果')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    output = getattr(args, 'output', None)
    
    commands = {
        'scan': lambda: cmd_scan(args.target, args.ports, output, args.verbose, args.timing, args.service, args.os),
        'ping': lambda: cmd_ping(args.target, args.count, output),
        'traceroute': lambda: cmd_traceroute(args.target, output),
        'mtr': lambda: cmd_mtr(args.target, args.count, output),
        'curl': lambda: cmd_curl(args.url, args.method, args.data, {}, output, not args.no_follow),
        'wget': lambda: cmd_wget(args.url, args.output, args.mirror),
        'nc': lambda: cmd_netcat(args.target, args.port, args.mode, output),
        'ss': lambda: cmd_ss(args.args, output),
        'netstat': lambda: cmd_netstat(args.args, output),
        'dig': lambda: cmd_dig(args.domain, args.record_type, args.server, output),
        'nslookup': lambda: cmd_nslookup(args.domain, args.server, output),
        'host': lambda: cmd_host(args.domain, output),
        'whois': lambda: cmd_whois(args.domain, output),
        'tcpdump': lambda: cmd_tcpdump(args.interface, args.count, args.host, args.port, output),
        'ngrep': lambda: cmd_ngrep(args.pattern, args.interface, args.host, args.port, output),
        'iperf3': lambda: cmd_iperf(args.target, args.client, args.port, args.time, output),
        'ip-addr': lambda: cmd_ip_addr(output),
        'ip-route': lambda: cmd_ip_route(output),
        'ifconfig': lambda: cmd_ifconfig(args.interface, output),
        'route': lambda: cmd_route_table(output),
        'arp': lambda: cmd_arp(output),
        'telnet': lambda: cmd_telnet(args.host, args.port, output),
        'ftp': lambda: cmd_ftp(args.host, args.user, args.password, output),
    }
    
    if args.command in commands:
        stdout, code = commands[args.command]()
        if stdout:
            print(stdout)
        if code != 0:
            sys.exit(code)
    else:
        print(f"未知命令: {args.command}")


if __name__ == '__main__':
    main()
