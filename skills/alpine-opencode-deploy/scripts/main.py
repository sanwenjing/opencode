# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os

OUTPUT_DIR = os.getcwd()


def get_output_path(filename: str) -> str:
    """获取输出文件的完整路径（保存到当前工作目录）"""
    return os.path.join(OUTPUT_DIR, filename)


def save_deployment_log(content: str) -> str:
    """保存部署日志"""
    log_file = get_output_path("opencode_deployment.log")
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(content)
    return log_file


import paramiko


def find_opencode(ssh) -> str | None:
    """查找OpenCode可执行文件"""
    # 先检查常见路径
    common_paths = [
        '/usr/local/bin/opencode',
        '/usr/bin/opencode',
        '/root/.opencode/bin/opencode',
    ]
    
    for path in common_paths:
        stdin, stdout, stderr = ssh.exec_command(f'test -x "{path}" && echo "exists"')
        if stdout.read().decode('utf-8').strip() == 'exists':
            stdin, stdout, stderr = ssh.exec_command(f'{path} --version 2>&1')
            version = stdout.read().decode('utf-8').strip()
            if 'v' in version:
                return path
    
    # 模糊搜索
    stdin, stdout, stderr = ssh.exec_command(
        'find /usr/lib/node_modules/opencode-ai -name opencode -type f 2>/dev/null'
    )
    paths = stdout.read().decode('utf-8').strip().split('\n')
    
    for path in paths:
        if path.strip():
            stdin, stdout, stderr = ssh.exec_command(f'{path.strip()} --version 2>&1')
            version = stdout.read().decode('utf-8').strip()
            if '1.1' in version:
                return path.strip()
    
    return None


def deploy_opencode(hostname: str, port: int, username: str, password: str) -> dict:
    """
    在Alpine Linux上部署OpenCode（成功经验优化版）
    
    部署步骤（2026-02-08验证成功）：
    1. SSH连接
    2. 安装bash和curl
    3. 下载完整Node.js包（x64版本，包含npm）
    4. 解压安装到/usr/local
    5. npm install -g opencode-ai
    6. 找到musl版本的opencode
    7. 创建符号链接
    """
    result = {
        "success": False,
        "hostname": hostname,
        "port": port,
        "node_version": None,
        "opencode_path": None,
        "opencode_version": None,
        "error": None,
        "log_file": None
    }
    
    log_lines = []
    log_lines.append("=" * 60)
    log_lines.append("OpenCode部署日志")
    log_lines.append(f"目标服务器: {hostname}:{port}")
    log_lines.append("=" * 60)
    
    try:
        print(f"连接 {hostname}:{port}...")
        log_lines.append(f"[1/6] 连接 {hostname}:{port}...")
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port=port, username=username, password=password, timeout=30)
        print("SSH连接成功!")
        log_lines.append("SSH连接成功!")
        
        # Step 1: 安装工具
        print("\n[2/6] 安装 bash 和 curl...")
        log_lines.append("[2/6] 安装 bash 和 curl...")
        stdin, stdout, stderr = ssh.exec_command('apk add --no-cache bash curl 2>&1', timeout=60)
        print(stdout.read().decode('utf-8'))
        
        # Step 2: 下载完整Node.js
        print("\n[3/6] 下载完整Node.js包...")
        log_lines.append("[3/6] 下载完整Node.js包...")
        
        cmd = """\
cd /tmp && \
rm -f node.tar.* 2>/dev/null && \
curl -L -o node.tar.xz "https://nodejs.org/dist/v20.10.0/node-v20.10.0-linux-x64.tar.xz" 2>&1 | tail -3"""
        
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=300)
        output = stdout.read().decode('utf-8')
        print(output)
        log_lines.append(output)
        
        # Step 3: 解压安装
        print("\n[4/6] 解压安装Node.js和npm...")
        log_lines.append("[4/6] 解压安装Node.js和npm...")
        
        cmd2 = """\
cd /tmp && \
tar -xf node.tar.xz && \
cp -r node-v20.10.0-linux-x64/bin/* /usr/local/bin/ && \
cp -r node-v20.10.0-linux-x64/lib/* /usr/local/lib/ && \
node --version && npm --version"""
        
        stdin, stdout, stderr = ssh.exec_command(cmd2, timeout=120)
        output = stdout.read().decode('utf-8')
        print(output)
        log_lines.append(output)
        result["node_version"] = "v20.10.0"
        
        # Step 4: 安装OpenCode
        print("\n[5/6] 安装 OpenCode...")
        log_lines.append("[5/6] 安装 OpenCode...")
        
        stdin, stdout, stderr = ssh.exec_command(
            'npm install -g opencode-ai 2>&1 && echo "NPM_SUCCESS"',
            timeout=300
        )
        output = stdout.read().decode('utf-8')
        print(output)
        log_lines.append(output)
        
        # Step 5: 找到正确的musl版本
        print("\n[6/6] 查找正确的OpenCode...")
        log_lines.append("[6/6] 查找正确的OpenCode...")
        
        opencode_path = find_opencode(ssh)
        
        if opencode_path:
            print(f"找到: {opencode_path}")
            log_lines.append(f"找到: {opencode_path}")
            
            stdin, stdout, stderr = ssh.exec_command(f'{opencode_path} --version')
            version = stdout.read().decode('utf-8').strip()
            print(f"版本: {version}")
            log_lines.append(f"版本: {version}")
            
            # 创建符号链接
            ssh.exec_command(f'ln -sf {opencode_path} /usr/local/bin/opencode 2>&1')
            ssh.exec_command(f'ln -sf {opencode_path} /usr/bin/opencode 2>&1')
            
            # 验证
            stdin, stdout, stderr = ssh.exec_command('opencode --version')
            final_version = stdout.read().decode('utf-8').strip()
            
            if final_version and '1.1' in final_version:
                result["success"] = True
                result["opencode_path"] = opencode_path
                result["opencode_version"] = final_version
            else:
                result["error"] = "版本验证失败"
        else:
            print("未找到OpenCode")
            log_lines.append("未找到OpenCode")
            result["error"] = "未找到OpenCode可执行文件"
        
        # 输出使用说明
        log_lines.append("")
        log_lines.append("=" * 60)
        log_lines.append("使用说明")
        log_lines.append("=" * 60)
        log_lines.append(f"SSH登录: ssh {username}@{hostname} -p {port}")
        log_lines.append(f"密码: {password}")
        log_lines.append("使用命令: opencode")
        log_lines.append("=" * 60)
        
        ssh.close()
        
    except Exception as e:
        error_msg = str(e)
        print(f"错误: {error_msg}")
        log_lines.append(f"错误: {error_msg}")
        result["error"] = error_msg
    
    # 保存日志
    log_content = '\n'.join(log_lines)
    log_file = save_deployment_log(log_content)
    result["log_file"] = log_file
    print(f"\n日志保存: {log_file}")
    
    return result


def main():
    """主函数"""
    print("=" * 60)
    print("OpenCode 远程部署工具")
    print("=" * 60)
    
    # 获取服务器配置
    print("\n请输入目标服务器信息:")
    
    hostname = input("服务器地址 (默认: 192.168.31.150): ").strip()
    if not hostname:
        hostname = "192.168.31.150"
    
    port_input = input("SSH端口 (默认: 2222): ").strip()
    port = int(port_input) if port_input else 2222
    
    username = input("用户名 (默认: root): ").strip()
    if not username:
        username = "root"
    
    password = input("密码 (默认: admin): ").strip()
    if not password:
        password = "admin"
    
    # 执行部署
    print("\n" + "=" * 60)
    print("开始部署...")
    print("=" * 60)
    
    result = deploy_opencode(
        hostname=hostname,
        port=port,
        username=username,
        password=password
    )
    
    # 输出结果
    print("\n" + "=" * 60)
    print("部署结果")
    print("=" * 60)
    print(f"服务器: {result['hostname']}:{result['port']}")
    print(f"Node.js版本: {result['node_version']}")
    print(f"OpenCode路径: {result['opencode_path']}")
    print(f"OpenCode版本: {result['opencode_version']}")
    print(f"部署状态: {'成功' if result['success'] else '失败'}")
    if result['error']:
        print(f"错误信息: {result['error']}")
    print(f"日志文件: {result['log_file']}")
    
    if result['success']:
        print("\n" + "=" * 60)
        print("使用说明")
        print("=" * 60)
        print(f"SSH登录: ssh {username}@{hostname} -p {port}")
        print(f"密码: {password}")
        print("使用命令: opencode")
        print("=" * 60)
    
    return result


if __name__ == '__main__':
    main()
