# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import subprocess
import time
import sys
from datetime import datetime

# 配置项
DEFAULT_MAX_RETRIES = 20  # 默认重试次数
DEFAULT_TIMEOUT = 300  # 单次git push超时时间（秒），5分钟


def run_git_push_with_output(timeout=DEFAULT_TIMEOUT):
    """
    执行git push并实时输出过程到控制台
    
    参数:
        timeout: 单次执行超时时间（秒）
    
    返回:
        (returncode, stdout, stderr, is_uptodate)
    """
    try:
        # 使用Popen实时输出
        process = subprocess.Popen(
            ['git', 'push'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            bufsize=1,
            universal_newlines=True
        )
        
        stdout_lines = []
        stderr_lines = []
        start_time = time.time()
        
        # 实时读取stdout
        if process.stdout:
            for line in process.stdout:
                line = line.rstrip()
                if line:
                    stdout_lines.append(line)
                    print(f"  [stdout] {line}")
                    sys.stdout.flush()
                
                # 检查超时
                if time.time() - start_time > timeout:
                    print(f"\n  [警告] 执行超过{timeout}秒，强制终止")
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except:
                        process.kill()
                    return -2, '\n'.join(stdout_lines), f"执行超时（>{timeout}秒）", False
        
        # 实时读取stderr
        if process.stderr:
            for line in process.stderr:
                line = line.rstrip()
                if line:
                    stderr_lines.append(line)
                    print(f"  [stderr] {line}")
                    sys.stderr.flush()
                
                # 检查超时
                if time.time() - start_time > timeout:
                    print(f"\n  [警告] 执行超过{timeout}秒，强制终止")
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except:
                        process.kill()
                    return -2, '\n'.join(stdout_lines), f"执行超时（>{timeout}秒）\n" + '\n'.join(stderr_lines), False
        
        # 等待进程完成，设置总体超时
        remaining_time = max(1, timeout - (time.time() - start_time))
        try:
            returncode = process.wait(timeout=remaining_time)
        except subprocess.TimeoutExpired:
            print(f"\n  [警告] 执行超过{timeout}秒，强制终止")
            process.terminate()
            try:
                process.wait(timeout=5)
            except:
                process.kill()
            return -2, '\n'.join(stdout_lines), f"执行超时（>{timeout}秒）", False
        
        stdout = '\n'.join(stdout_lines)
        stderr = '\n'.join(stderr_lines)
        
        # 检查是否包含 "Everything up-to-date"
        output = stdout + stderr
        is_uptodate = 'Everything up-to-date' in output
        
        return returncode, stdout, stderr, is_uptodate
        
    except Exception as e:
        print(f"  [错误] 执行异常: {e}")
        return -1, '', str(e), False


def run_git_push(max_retries=DEFAULT_MAX_RETRIES, delay=5, verbose=True):
    """
    持续重试git push命令直到成功（实时输出过程）
    
    参数:
        max_retries: 最大重试次数，None表示无限重试
        delay: 每次重试之间的等待时间（秒）
        verbose: 是否显示详细输出
    """
    retry_count = 0
    
    if verbose:
        print("=" * 60)
        print("         Git Push 自动重试工具")
        print("=" * 60)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        try:
            pwd_result = subprocess.run(['pwd'], capture_output=True, text=True, shell=True)
            print(f"工作目录: {pwd_result.stdout.strip()}")
        except:
            pass
        print(f"重试间隔: {delay}秒")
        print(f"单次超时: {DEFAULT_TIMEOUT}秒（{DEFAULT_TIMEOUT//60}分钟）")
        if max_retries:
            print(f"最大重试次数: {max_retries}")
        else:
            print("最大重试次数: 无限重试")
        print("=" * 60)
        print()
    
    while True:
        retry_count += 1
        
        if max_retries and retry_count > max_retries:
            print(f"\n✗ 已达到最大重试次数 ({max_retries})，停止重试")
            return False
        
        print(f"\n[{retry_count}] {datetime.now().strftime('%H:%M:%S')} - 开始执行 git push...")
        print("-" * 50)
        
        try:
            # 执行git push并实时输出
            returncode, stdout, stderr, is_uptodate = run_git_push_with_output()
            
            print("-" * 50)
            
            # 检查是否成功
            if returncode == 0:
                if is_uptodate:
                    print(f"\n✓ 检测到已经推送过（Everything up-to-date）")
                    print(f"  检测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"  总尝试次数: {retry_count}")
                    print(f"\n无需重复推送，退出脚本。")
                else:
                    print(f"\n✓ Git push 成功！")
                    print(f"  成功时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"  总重试次数: {retry_count}")
                return True
            else:
                # 推送失败
                print(f"\n✗ 推送失败 (返回码: {returncode})")
                if stderr:
                    # 只显示错误的第一行，避免过多输出
                    error_first_line = stderr.strip().split('\n')[0]
                    print(f"  错误: {error_first_line[:100]}")
                print(f"\n  等待 {delay} 秒后重试...")
                
                # 等待指定时间后重试
                time.sleep(delay)
                
        except FileNotFoundError:
            print("\n✗ 错误: 未找到git命令，请确保Git已安装并添加到系统PATH")
            return False
        except KeyboardInterrupt:
            print(f"\n\n⚠ 用户中断，共重试 {retry_count} 次")
            return False
        except Exception as e:
            print(f"\n✗ 发生异常: {e}")
            print(f"  等待 {delay} 秒后重试...")
            time.sleep(delay)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description=f'自动重试git push直到成功（实时输出过程，单次超时{DEFAULT_TIMEOUT}秒）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
使用示例:
  # 默认重试{DEFAULT_MAX_RETRIES}次，每5秒尝试一次，单次超时{DEFAULT_TIMEOUT}秒（5分钟）
  python git_push_retry.py
  
  # 最多重试10次
  python git_push_retry.py -m 10
  
  # 设置重试间隔为3秒
  python git_push_retry.py -d 3
  
  # 静默模式（只显示成功或最终失败）
  python git_push_retry.py -q
        """
    )
    
    parser.add_argument(
        '-m', '--max-retries',
        type=int,
        default=DEFAULT_MAX_RETRIES,
        help=f'最大重试次数（默认：{DEFAULT_MAX_RETRIES}）'
    )
    
    parser.add_argument(
        '-d', '--delay',
        type=int,
        default=5,
        help='重试间隔时间（秒，默认：5）'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='静默模式（减少输出信息）'
    )
    
    args = parser.parse_args()
    
    # 验证参数
    if args.delay < 1:
        print("✗ 错误: 重试间隔时间必须大于0秒")
        sys.exit(1)
    
    if args.max_retries is not None and args.max_retries < 1:
        print("✗ 错误: 最大重试次数必须大于0")
        sys.exit(1)
    
    # 运行主程序
    success = run_git_push(
        max_retries=args.max_retries,
        delay=args.delay,
        verbose=not args.quiet
    )
    
    # 根据结果退出
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
