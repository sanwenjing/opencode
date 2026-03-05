# -*- coding: utf-8 -*-
"""
Nexa安装脚本上传与配置服务脚本

功能：
- 上传Nexa CLI安装脚本到远程主机
- 执行安装脚本
- 配置并启动systemd服务
- 设置开机自启

依赖说明：
- 本脚本依赖remote-manager技能进行远程文件上传和命令执行
- 确保remote-manager技能已安装且配置好远程主机信息
"""

import os
import sys
import argparse
import subprocess
import time
import logging

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def get_output_path(filename):
    """
    获取输出文件的完整路径
    规则：所有输出文件保存到当前工作目录，而不是技能安装目录
    """
    return os.path.join(os.getcwd(), filename)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='上传Nexa CLI安装脚本并配置开机启动服务',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 主机参数
    parser.add_argument('-h', '--host', required=True, help='远程主机名称或IP地址')
    parser.add_argument('-p', '--port', type=int, default=22, help='SSH端口（默认：22）')
    parser.add_argument('-u', '--username', default='root', help='SSH用户名（默认：root）')
    parser.add_argument('--password', help='SSH密码')
    parser.add_argument('-k', '--private-key', help='SSH私钥文件路径')
    
    # 安装参数
    parser.add_argument('-s', '--script-path', required=True, help='本地Nexa CLI安装脚本路径')
    parser.add_argument('--host-addr', default='0.0.0.0', help='服务监听地址（默认：0.0.0.0）')
    parser.add_argument('--listen-port', type=int, default=18181, help='服务监听端口（默认：18181）')
    parser.add_argument('--install-path', default='/usr/local/bin', help='Nexa安装路径（默认：/usr/local/bin）')
    parser.add_argument('--remote-temp-dir', default='/tmp', help='远程临时目录（默认：/tmp）')
    
    # 行为选项
    parser.add_argument('--upload-only', action='store_true', help='仅上传安装脚本，不执行安装')
    parser.add_argument('--install-only', action='store_true', help='仅执行安装，不上传脚本（脚本需已存在）')
    parser.add_argument('--no-service', action='store_true', help='不创建systemd服务')
    parser.add_argument('--service-name', default='nexa', help='服务名称（默认：nexa）')
    
    # 其他选项
    parser.add_argument('--skip-update', action='store_true', help='跳过版本检查')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    return parser.parse_args()


def load_remote_manager_script():
    """加载remote-manager技能的主脚本路径"""
    # 尝试多个可能的位置
    possible_paths = [
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'remote-manager', 'scripts', 'main.py'
        ),
        '/root/.config/opencode/skills/remote-manager/scripts/main.py',
        os.path.expanduser('~/.config/opencode/skills/remote-manager/scripts/main.py')
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None


def upload_script(args):
    """上传安装脚本到远程主机"""
    logger.info(f'开始上传安装脚本：{args.script_path}')
    
    remote_filename = os.path.join(
        args.remote_temp_dir, 
        os.path.basename(args.script_path)
    )
    
    # 检查remote-manager脚本是否存在
    remote_manager_path = load_remote_manager_script()
    
    if not remote_manager_path:
        logger.error('未找到remote-manager脚本，无法上传文件')
        return None
    
    logger.info(f'使用remote-manager脚本：{remote_manager_path}')
    
    # 使用remote-manager上传
    cmd = [
        sys.executable, remote_manager_path,
        'upload', '-n', args.host,
        '-s', args.script_path,
        '-d', remote_filename
    ]
    
    try:
        logger.info('执行上传命令...')
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            logger.info('脚本上传成功')
            return remote_filename
        else:
            logger.error(f'脚本上传失败：{result.stderr}')
            if result.stdout:
                logger.debug(f'标准输出：{result.stdout}')
            return None
    except subprocess.TimeoutExpired:
        logger.error('脚本上传超时')
        return None
    except Exception as e:
        logger.error(f'上传过程中发生错误：{str(e)}')
        return None


def check_remote_script_exists(args, remote_path):
    """检查远程主机上脚本是否存在"""
    remote_manager_path = load_remote_manager_script()
    
    if not remote_manager_path:
        return False
    
    cmd = [
        sys.executable, remote_manager_path,
        'exec', '-n', args.host,
        '-c', f'test -f {remote_path} && echo "exists" || echo "not found"'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if 'exists' in result.stdout:
            return True
        return False
    except Exception:
        return False


def execute_install(args, remote_script_path=None):
    """在远程主机上执行安装"""
    logger.info('开始执行安装脚本')
    
    remote_manager_path = load_remote_manager_script()
    
    if not remote_script_path:
        remote_script_path = os.path.join(
            args.remote_temp_dir,
            os.path.basename(args.script_path)
        )
    
    # 检查脚本是否存在
    if not check_remote_script_exists(args, remote_script_path):
        logger.error(f'远程脚本不存在：{remote_script_path}')
        return False
    
    logger.info(f'远程脚本路径：{remote_script_path}')
    
    # 执行安装脚本
    install_cmd = f'chmod +x {remote_script_path} && {remote_script_path}'
    
    cmd = [
        sys.executable, remote_manager_path,
        'exec', '-n', args.host,
        '-c', install_cmd
    ]
    
    try:
        logger.info('执行安装命令...')
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            logger.info('安装脚本执行成功')
            return True
        else:
            logger.error(f'安装脚本执行失败：{result.stderr}')
            if result.stdout:
                logger.debug(f'标准输出：{result.stdout}')
            return False
    except subprocess.TimeoutExpired:
        logger.error('安装脚本执行超时')
        return False
    except Exception as e:
        logger.error(f'安装过程中发生错误：{str(e)}')
        return False


def create_systemd_service(args):
    """创建并配置systemd服务"""
    logger.info('创建systemd服务')
    
    remote_manager_path = load_remote_manager_script()
    
    if not remote_manager_path:
        return False
    
    # 生成服务文件内容
    service_content = f'''[Unit]
Description=Nexa AI Service
After=network.target

[Service]
Type=simple
User=root
ExecStart={args.install_path}/nexa serve --host {args.host_addr}:{args.listen_port}
Restart=on-failure
RestartSec=5
Environment=NEXA_HOST={args.host_addr}:{args.listen_port}

[Install]
WantedBy=multi-user.target
'''
    
    service_file = '/etc/systemd/system/nexa.service'
    
    # 创建服务文件
    create_cmd = f'cat > {service_file} << \'EOF\'\n{service_content}EOF'
    
    cmd = [
        sys.executable, remote_manager_path,
        'exec', '-n', args.host,
        '-c', create_cmd
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            logger.error(f'创建服务文件失败：{result.stderr}')
            return False
        
        logger.info('服务文件创建成功')
    except Exception as e:
        logger.error(f'创建服务文件时发生错误：{str(e)}')
        return False
    
    # 启用并启动服务
    enable_cmd = 'systemctl daemon-reload && systemctl enable nexa && systemctl start nexa'
    
    cmd = [
        sys.executable, remote_manager_path,
        'exec', '-n', args.host,
        '-c', enable_cmd
    ]
    
    try:
        logger.info('启用并启动服务...')
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            logger.info('服务已启用并启动')
            
            # 验证服务状态
            return verify_service_status(args)
        else:
            logger.error(f'启用服务失败：{result.stderr}')
            return False
    except Exception as e:
        logger.error(f'启用服务时发生错误：{str(e)}')
        return False


def verify_service_status(args):
    """验证服务状态"""
    logger.info('验证服务状态')
    
    remote_manager_path = load_remote_manager_script()
    
    if not remote_manager_path:
        return False
    
    # 检查systemctl状态和端口监听
    status_cmd = f'systemctl status nexa && ss -tlnp | grep {args.listen_port}'
    
    cmd = [
        sys.executable, remote_manager_path,
        'exec', '-n', args.host,
        '-c', status_cmd
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # 检查服务是否active (running)
        if 'active (running)' in result.stdout:
            logger.info('服务运行正常')
            return True
        else:
            logger.warning('服务可能未正常运行，请检查')
            logger.debug(f'服务状态输出：{result.stdout}')
            if result.stderr:
                logger.debug(f'错误输出：{result.stderr}')
            return False
    except Exception as e:
        logger.error(f'验证服务状态时发生错误：{str(e)}')
        return False


def check_nexa_version(args):
    """检查Nexa安装版本"""
    logger.info('检查Nexa版本')
    
    remote_manager_path = load_remote_manager_script()
    
    if not remote_manager_path:
        return False
    
    cmd = [
        sys.executable, remote_manager_path,
        'exec', '-n', args.host,
        '-c', 'nexa version'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            version_info = result.stdout.strip()
            logger.info(f'Nexa版本信息：{version_info}')
            
            # 提取版本号
            for line in version_info.split('\n'):
                if 'Version' in line:
                    logger.info(line.strip())
            return True
        else:
            logger.warning('无法获取Nexa版本信息')
            return False
    except Exception as e:
        logger.error(f'检查版本时发生错误：{str(e)}')
        return False


def main():
    """主函数"""
    args = parse_args()
    
    # 检查本地脚本文件
    if not args.install_only:
        if not os.path.exists(args.script_path):
            logger.error(f'安装脚本不存在：{args.script_path}')
            print(f'错误：安装脚本不存在：{args.script_path}', file=sys.stderr)
            sys.exit(1)
        
        file_size = os.path.getsize(args.script_path) / (1024 * 1024)
        logger.info(f'本地安装脚本：{args.script_path}')
        logger.info(f'文件大小：{file_size:.2f} MB')
    
    # 远程主机信息
    logger.info(f'目标主机：{args.host}')
    logger.info(f'监听地址：{args.host_addr}:{args.listen_port}')
    logger.info('=' * 50)
    
    # 步骤1：上传安装脚本
    remote_script_path = None
    if not args.install_only:
        print('步骤1：上传安装脚本...')
        remote_script_path = upload_script(args)
        if not remote_script_path:
            logger.error('上传安装脚本失败')
            sys.exit(1)
        print('✓ 脚本上传成功')
    else:
        remote_script_path = os.path.join(
            args.remote_temp_dir,
            os.path.basename(args.script_path)
        )
        print(f'使用现有脚本：{remote_script_path}')
    
    # 步骤2：执行安装脚本
    if not args.upload_only:
        print('\n步骤2：执行安装脚本...')
        if execute_install(args, remote_script_path):
            print('✓ 安装脚本执行成功')
            # 检查版本
            check_nexa_version(args)
        else:
            logger.error('执行安装脚本失败')
            sys.exit(1)
    
    # 步骤3：创建systemd服务
    if not args.no_service and not args.upload_only:
        print('\n步骤3：创建systemd服务...')
        if create_systemd_service(args):
            print('✓ 服务配置完成')
        else:
            logger.error('创建systemd服务失败')
            sys.exit(1)
    
    # 总结
    print('\n' + '=' * 50)
    print('安装完成总结')
    print('=' * 50)
    print(f'目标主机：{args.host}')
    print(f'服务地址：http://{args.host_addr}:{args.listen_port}')
    print(f'API文档：http://{args.host_addr}:{args.listen_port}/docs')
    print(f'Web UI：http://{args.host_addr}:{args.listen_port}/docs/ui')
    print(f'\n服务管理命令：')
    print(f'  查看状态：systemctl status nexa')
    print(f'  启动服务：systemctl start nexa')
    print(f'  停止服务：systemctl stop nexa')
    print(f'  重启服务：systemctl restart nexa')
    print('=' * 50)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())