# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import yaml
import argparse
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path

try:
    import paramiko
except ImportError:
    print("错误: 请先安装paramiko库")
    print("运行: pip install paramiko cryptography")
    sys.exit(1)


@dataclass
class Host:
    name: str
    host: str
    port: int = 22
    username: str = "root"
    password: Optional[str] = None
    private_key_path: Optional[str] = None
    remark: str = ""
    purpose: str = ""
    os_version: str = ""
    enabled: bool = True

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Host':
        return cls(
            name=data.get('name', ''),
            host=data.get('host', ''),
            port=data.get('port', 22),
            username=data.get('username', 'root'),
            password=data.get('password'),
            private_key_path=data.get('private_key_path'),
            remark=data.get('remark', ''),
            purpose=data.get('purpose', ''),
            os_version=data.get('os_version', ''),
            enabled=data.get('enabled', True)
        )


def _find_hosts_file() -> str:
    """查找hosts.yaml配置文件，优先顺序：当前工作目录 > 技能安装目录"""
    candidates = [
        os.path.join(os.getcwd(), "hosts.yaml"),
    ]
    
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates.append(os.path.join(skill_dir, "config", "hosts.yaml"))
    
    for path in candidates:
        if os.path.exists(path):
            return path
    
    return candidates[0]


class HostManager:
    def __init__(self, hosts_file: str = None):
        if hosts_file is None:
            hosts_file = _find_hosts_file()
        self.hosts_file = hosts_file
        self.hosts: Dict[str, Host] = {}
        self.load_hosts()

    def load_hosts(self) -> None:
        """加载主机列表"""
        if os.path.exists(self.hosts_file):
            try:
                with open(self.hosts_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and 'hosts' in data:
                        for host_data in data['hosts']:
                            host = Host.from_dict(host_data)
                            self.hosts[host.name] = host
            except Exception as e:
                print(f"警告: 加载主机列表失败: {e}")

    def save_hosts(self) -> None:
        """保存主机列表"""
        data = {
            'updated': datetime.now().isoformat(),
            'hosts': [host.to_dict() for host in self.hosts.values()]
        }
        with open(self.hosts_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False)

    def add_host(self, host: Host, fetch_os: bool = True) -> bool:
        """添加主机"""
        if host.name in self.hosts:
            print(f"错误: 主机 '{host.name}' 已存在")
            return False
        
        if fetch_os and host.enabled:
            print(f"正在获取 {host.name} 的操作系统版本...")
            os_version = get_host_os_version(host)
            if os_version:
                host.os_version = os_version
                print(f"  操作系统: {os_version}")
        
        self.hosts[host.name] = host
        self.save_hosts()
        print(f"成功添加主机: {host.name} ({host.host}:{host.port})")
        return True

    def refresh_os_version(self, name: str) -> bool:
        """刷新指定主机的操作系统版本"""
        if name not in self.hosts:
            print(f"错误: 主机 '{name}' 不存在")
            return False
        
        host = self.hosts[name]
        print(f"正在获取 {name} 的操作系统版本...")
        os_version = get_host_os_version(host)
        
        if os_version:
            host.os_version = os_version
            self.save_hosts()
            print(f"  操作系统已更新: {os_version}")
            return True
        else:
            print(f"  无法获取操作系统版本")
            return False

    def refresh_all_os_versions(self) -> None:
        """刷新所有主机的操作系统版本"""
        count = 0
        for name, host in self.hosts.items():
            if host.enabled:
                if self.refresh_os_version(name):
                    count += 1
        print(f"成功刷新 {count}/{len(self.hosts)} 个主机的操作系统版本")

    def remove_host(self, name: str) -> bool:
        """删除主机"""
        if name not in self.hosts:
            print(f"错误: 主机 '{name}' 不存在")
            return False
        del self.hosts[name]
        self.save_hosts()
        print(f"成功删除主机: {name}")
        return True

    def update_host(self, name: str, **kwargs) -> bool:
        """更新主机信息"""
        if name not in self.hosts:
            print(f"错误: 主机 '{name}' 不存在")
            return False
        host = self.hosts[name]
        for key, value in kwargs.items():
            if hasattr(host, key) and value is not None:
                setattr(host, key, value)
        self.save_hosts()
        print(f"成功更新主机: {name}")
        return True

    def list_hosts(self, show_passwords: bool = False) -> None:
        """列出所有主机"""
        if not self.hosts:
            print("当前没有配置任何主机")
            return

        print("\n" + "=" * 140)
        print(f"{'名称':<20} {'地址':<25} {'端口':<6} {'用户名':<12} {'操作系统':<25} {'用途':<18} {'备注':<20} {'状态':<6}")
        print("-" * 140)

        for name, host in self.hosts.items():
            status = "启用" if host.enabled else "禁用"
            os_display = host.os_version if host.os_version else "未获取"
            print(f"{name:<20} {host.host:<25} {host.port:<6} {host.username:<12} {os_display:<25} {host.purpose:<18} {host.remark:<20} {status:<6}")

        print("=" * 140)
        print(f"总计: {len(self.hosts)} 个主机")

    def get_host(self, name: str) -> Optional[Host]:
        """获取指定主机"""
        return self.hosts.get(name)

    def get_all_enabled_hosts(self) -> List[Host]:
        """获取所有启用的主机"""
        return [h for h in self.hosts.values() if h.enabled]


class SSHExecutor:
    def __init__(self, host: Host, timeout: int = 30):
        self.host = host
        self.timeout = timeout
        self.client: Optional[paramiko.SSHClient] = None

    def connect(self) -> bool:
        """建立SSH连接"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            connect_params = {
                'hostname': self.host.host,
                'port': self.host.port,
                'username': self.host.username,
                'timeout': self.timeout,
                'allow_agent': False,
                'look_for_keys': False
            }

            if self.host.private_key_path and os.path.exists(self.host.private_key_path):
                key = paramiko.RSAKey.from_private_key_file(self.host.private_key_path)
                connect_params['pkey'] = key
            elif self.host.password:
                connect_params['password'] = self.host.password
            else:
                print(f"错误: 主机 {self.host.name} 未配置密码或私钥")
                return False

            self.client.connect(**connect_params)
            return True

        except Exception as e:
            print(f"连接失败 [{self.host.name}]: {str(e)}")
            return False

    def execute(self, command: str) -> tuple:
        """执行命令"""
        if not self.client:
            if not self.connect():
                return False, "", "连接失败"

        try:
            assert self.client is not None
            stdin, stdout, stderr = self.client.exec_command(command, timeout=self.timeout)
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode('utf-8', errors='replace')
            error = stderr.read().decode('utf-8', errors='replace')
            return exit_status == 0, output, error
        except Exception as e:
            return False, "", str(e)

    def close(self) -> None:
        """关闭连接"""
        if self.client:
            self.client.close()
            self.client = None

    def execute_and_close(self, command: str) -> tuple:
        """执行命令并关闭连接"""
        success, output, error = self.execute(command)
        self.close()
        return success, output, error

    def get_os_version(self) -> str:
        """获取操作系统版本"""
        success, output, _ = self.execute("cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'=' -f2 | tr -d '\"'")
        if success and output.strip():
            return output.strip()
        success, output, _ = self.execute("uname -sr")
        if success and output.strip():
            return output.strip()
        return "Unknown"


def get_host_os_version(host: Host) -> str:
    """获取主机的操作系统版本"""
    executor = SSHExecutor(host)
    os_version = executor.get_os_version()
    executor.close()
    return os_version


def batch_execute(manager: HostManager, command: str, hosts: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """批量执行命令"""
    if hosts is not None and len(hosts) > 0:
        target_hosts = []
        for name in hosts:
            host = manager.get_host(name)
            if host:
                target_hosts.append(host)
            else:
                print(f"警告: 主机 '{name}' 不存在")
    else:
        target_hosts = manager.get_all_enabled_hosts()

    if not target_hosts:
        print("没有可执行命令的目标主机")
        return []

    print(f"\n将在 {len(target_hosts)} 个主机上执行命令: {command}")
    print("=" * 100)

    results: List[Dict[str, Any]] = []
    for host in target_hosts:
        print(f"\n[{host.name}] {host.host}:{host.port}")
        print("-" * 50)

        executor = SSHExecutor(host)
        success, output, error = executor.execute(command)

        result = {
            'host': host.name,
            'host_address': host.host,
            'success': success,
            'output': output,
            'error': error
        }
        results.append(result)

        if success:
            print(f"✓ 执行成功")
            if output.strip():
                print(output)
        else:
            print(f"✗ 执行失败: {error}")

        executor.close()

    print("\n" + "=" * 100)
    print("执行摘要:")
    success_count = sum(1 for r in results if r['success'])
    print(f"  成功: {success_count}/{len(results)}")
    print(f"  失败: {len(results) - success_count}/{len(results)}")

    return results


def import_hosts_from_csv(manager: HostManager, csv_file: str) -> int:
    """从CSV文件导入主机"""
    import csv

    if not os.path.exists(csv_file):
        print(f"错误: 文件不存在: {csv_file}")
        return 0

    count = 0
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                host = Host(
                    name=row.get('name', '').strip(),
                    host=row.get('host', '').strip(),
                    port=int(row.get('port', 22)),
                    username=row.get('username', 'root').strip(),
                    password=row.get('password', '').strip() or None,
                    private_key_path=row.get('private_key_path', '').strip() or None,
                    remark=row.get('remark', '').strip(),
                    purpose=row.get('purpose', '').strip(),
                    enabled=row.get('enabled', 'true').lower() == 'true'
                )
                if host.name and host.host:
                    if manager.add_host(host):
                        count += 1
    except Exception as e:
        print(f"导入失败: {e}")
        return 0

    print(f"成功导入 {count} 个主机")
    return count


def export_hosts_to_csv(manager: HostManager, csv_file: str) -> None:
    """导出主机到CSV文件"""
    import csv

    fieldnames = ['name', 'host', 'port', 'username', 'password', 'private_key_path', 'remark', 'purpose', 'enabled']

    try:
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for host in manager.hosts.values():
                writer.writerow(host.to_dict())
        print(f"成功导出到: {csv_file}")
    except Exception as e:
        print(f"导出失败: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='批量管理远程SSH主机',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 列出所有主机
  python main.py list

  # 添加主机
  python main.py add -n server1 -h 192.168.1.100 -p 22 -u root -pwd yourpassword -p "Web服务器"

  # 删除主机
  python main.py remove -n server1

  # 更新主机
  python main.py update -n server1 -p 2222 -pwd newpassword

  # 批量执行命令
  python main.py exec -c "uptime" -n server1 server2

  # 批量执行OpenCode相关命令
  python main.py exec -c "cd /opt/opencode && git pull" -n all

  # 从CSV导入
  python main.py import -f hosts.csv

  # 导出到CSV
  python main.py export -f hosts_backup.csv

  # 导出执行结果
  python main.py exec -c "uptime" -o results.json
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    list_parser = subparsers.add_parser('list', help='列出所有主机')
    list_parser.add_argument('--show-passwords', '-s', action='store_true', help='显示密码')

    add_parser = subparsers.add_parser('add', help='添加新主机')
    add_parser.add_argument('--name', '-n', required=True, help='主机名称(唯一标识)')
    add_parser.add_argument('--host', required=True, help='主机地址/IP')
    add_parser.add_argument('--port', '-p', type=int, default=22, help='SSH端口 (默认: 22)')
    add_parser.add_argument('--username', '-u', default='root', help='用户名 (默认: root)')
    add_parser.add_argument('--password', '-pwd', help='密码')
    add_parser.add_argument('--private-key', '-k', help='私钥文件路径')
    add_parser.add_argument('--purpose', '-P', default='', help='用途说明')
    add_parser.add_argument('--remark', '-r', default='', help='备注信息')

    update_parser = subparsers.add_parser('update', help='更新主机信息')
    update_parser.add_argument('--name', '-n', required=True, help='要更新的主机名称')
    update_parser.add_argument('--host', help='新地址')
    update_parser.add_argument('--port', '-p', type=int, help='新端口')
    update_parser.add_argument('--username', '-u', help='新用户名')
    update_parser.add_argument('--password', '-pwd', help='新密码')
    update_parser.add_argument('--purpose', '-P', help='新用途')
    update_parser.add_argument('--remark', '-r', help='新备注')
    update_parser.add_argument('--enabled', '-e', type=str, choices=['true', 'false'], help='启用/禁用')

    remove_parser = subparsers.add_parser('remove', help='删除主机')
    remove_parser.add_argument('--name', '-n', required=True, help='要删除的主机名称')

    exec_parser = subparsers.add_parser('exec', help='批量执行命令')
    exec_parser.add_argument('--cmd', '-c', required=True, dest='cmd', help='要执行的命令')
    exec_parser.add_argument('--names', '-n', nargs='*', dest='target_names', help='目标主机名称(留空则执行所有启用主机)')
    exec_parser.add_argument('--output', '-o', help='输出结果到文件(JSON格式)')

    import_parser = subparsers.add_parser('import', help='从CSV文件导入主机')
    import_parser.add_argument('--file', '-f', required=True, help='CSV文件路径')

    export_parser = subparsers.add_parser('export', help='导出主机到CSV文件')
    export_parser.add_argument('--file', '-f', required=True, help='输出CSV文件路径')

    refresh_parser = subparsers.add_parser('refresh', help='刷新主机操作系统版本')
    refresh_parser.add_argument('--name', '-n', help='指定主机名称(留空则刷新所有主机)')

    args = parser.parse_args()

    manager = HostManager()

    if args.command == 'list':
        manager.list_hosts(show_passwords=args.show_passwords)

    elif args.command == 'add':
        host = Host(
            name=args.name,
            host=args.host,
            port=args.port,
            username=args.username,
            password=args.password,
            private_key_path=args.private_key,
            purpose=args.purpose,
            remark=args.remark
        )
        manager.add_host(host)

    elif args.command == 'remove':
        manager.remove_host(args.name)

    elif args.command == 'update':
        update_kwargs = {}
        if args.host:
            update_kwargs['host'] = args.host
        if args.port:
            update_kwargs['port'] = args.port
        if args.username:
            update_kwargs['username'] = args.username
        if args.password:
            update_kwargs['password'] = args.password
        if args.purpose:
            update_kwargs['purpose'] = args.purpose
        if args.remark:
            update_kwargs['remark'] = args.remark
        if args.enabled:
            update_kwargs['enabled'] = args.enabled == 'true'

        if update_kwargs:
            manager.update_host(args.name, **update_kwargs)
        else:
            print("错误: 未指定任何要更新的内容")

    elif args.command == 'exec':
        results = batch_execute(manager, args.cmd, args.target_names)

        if args.output and results:
            output_file = os.path.join(os.getcwd(), args.output)
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n结果已保存到: {output_file}")

    elif args.command == 'import':
        import_hosts_from_csv(manager, args.file)

    elif args.command == 'export':
        export_hosts_to_csv(manager, args.file)

    elif args.command == 'refresh':
        if args.name:
            manager.refresh_os_version(args.name)
        else:
            manager.refresh_all_os_versions()

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
