# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import argparse
import subprocess
import time
from datetime import datetime, timedelta


def send_email(subject: str, body: str) -> bool:
    """调用 email-sender 技能发送邮件"""
    email_sender_path = os.path.join(
        os.path.expanduser("~"), ".config", "opencode", "skills", "email-sender", "scripts", "main.py"
    )
    
    if not os.path.exists(email_sender_path):
        print(f"警告: email-sender 技能不存在，跳过邮件发送")
        return False
    
    result = subprocess.run(
        [sys.executable, email_sender_path, "-s", subject, "-b", body, "-y"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("邮件发送成功")
        return True
    else:
        print(f"邮件发送失败: {result.stderr}")
        return False


def check_needs_push(repo_path: str) -> bool:
    """检查是否有需要 push 的内容"""
    result = subprocess.run(
        ['git', 'status', '--porcelain'],
        capture_output=True,
        text=True,
        cwd=repo_path
    )
    
    if result.returncode != 0:
        return False
    
    uncommitted = result.stdout.strip()
    
    if uncommitted:
        print(f"存在未提交的更改:")
        print(uncommitted)
        return False
    
    result = subprocess.run(
        ['git', 'rev-list', '@{u}..HEAD', '--count'],
        capture_output=True,
        text=True,
        cwd=repo_path
    )
    
    if result.returncode == 0 and result.stdout.strip():
        commits_behind = int(result.stdout.strip())
        if commits_behind > 0:
            print(f"本地领先远程 {commits_behind} 个提交，需要 push")
            return True
    
    result = subprocess.run(
        ['git', 'rev-list', 'HEAD..@{u}', '--count'],
        capture_output=True,
        text=True,
        cwd=repo_path
    )
    
    if result.returncode == 0 and result.stdout.strip():
        commits_ahead = int(result.stdout.strip())
        if commits_ahead > 0:
            print(f"本地落后远程 {commits_ahead} 个提交，需要 pull")
            return False
    
    print("没有需要 push 的内容")
    return False


def main():
    parser = argparse.ArgumentParser(description='执行git push并发送邮件通知')
    parser.add_argument('--repo', '-r', type=str, default='~/.config/opencode', 
                        help='仓库文件夹路径 (默认: ~/.config/opencode)')
    parser.add_argument('--timeout', '-t', type=int, default=1800, 
                        help='最大等待时间，秒为单位 (默认: 1800秒=30分钟)')
    parser.add_argument('--interval', '-i', type=int, default=5, 
                        help='重试间隔时间，秒为单位 (默认: 5秒)')
    parser.add_argument('--no-email', action='store_true', 
                        help='不发送邮件通知')
    args = parser.parse_args()
    
    repo_path = os.path.expanduser(args.repo)
    max_timeout = args.timeout
    retry_interval = args.interval
    
    print(f"当前目录: {os.getcwd()}")
    print(f"仓库路径: {repo_path}")
    print(f"最大等待时间: {max_timeout}秒 ({max_timeout//60}分钟)")
    print(f"重试间隔: {retry_interval}秒")
    print("-" * 40)
    
    if not os.path.isdir(repo_path):
        print(f"错误: 目录不存在: {repo_path}")
        sys.exit(1)
    
    print("检查是否有需要 push 的内容...")
    if not check_needs_push(repo_path):
        print("没有需要 push 的内容，退出")
        print(f"当前目录保持不变: {os.getcwd()}")
        return
    
    print("\n开始执行 git push ...")
    print("-" * 40)
    
    start_time = datetime.now()
    attempt = 0
    last_error = None
    
    while True:
        attempt += 1
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 第 {attempt} 次尝试 (已耗时: {int(elapsed)}秒)")
        
        result = subprocess.run(['git', 'push'], capture_output=True, text=True, cwd=repo_path)
        
        if result.returncode == 0:
            print("\n--- Git Push 成功 ---")
            print(result.stdout)
            print(f"\nGit push 执行成功! 共尝试 {attempt} 次")
            print(f"总耗时: {int(elapsed)}秒")
            print(f"当前目录保持不变: {os.getcwd()}")
            
            if not args.no_email:
                repo_name = os.path.basename(repo_path)
                subject = f"Git Push 成功 - {repo_name}"
                body = f"""
Git Push 操作已成功完成！

仓库: {repo_path}
尝试次数: {attempt}
总耗时: {int(elapsed)}秒
完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                print("\n正在发送邮件通知...")
                send_email(subject, body)
            
            return
        
        last_error = result.stderr or result.stdout
        print(f"--- 失败 (退出码: {result.returncode}) ---")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if elapsed >= max_timeout:
            print(f"\n已达到最大等待时间 {max_timeout}秒 ({max_timeout//60}分钟)")
            print(f"最终失败，共尝试 {attempt} 次")
            print(f"当前目录保持不变: {os.getcwd()}")
            
            if not args.no_email:
                repo_name = os.path.basename(repo_path)
                subject = f"Git Push 失败 - {repo_name}"
                body = f"""
Git Push 操作失败！

仓库: {repo_path}
尝试次数: {attempt}
总耗时: {int(elapsed)}秒
失败时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
错误信息: {last_error[:500]}
"""
                print("\n正在发送邮件通知...")
                send_email(subject, body)
            
            sys.exit(1)
        
        remaining = max_timeout - elapsed
        wait_time = min(retry_interval, remaining)
        print(f"\n等待 {int(wait_time)} 秒后重试... (剩余: {int(remaining)}秒)")
        time.sleep(wait_time)


if __name__ == '__main__':
    main()
