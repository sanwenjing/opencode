# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import argparse
import subprocess
import sys

REMOTE_SKILL = "/root/.config/opencode/skills/remote-manager/scripts/main.py"

def run_remote_command(host_name, command):
    cmd = ["python3", REMOTE_SKILL, "exec", "-n", host_name, "-c", command]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return result.stdout + result.stderr

def main():
    parser = argparse.ArgumentParser(description="OpenClaw配置管理工具")
    parser.add_argument("-n", "--host", default="node-2224", help="目标主机名称")
    parser.add_argument("command", choices=["models", "config", "gateway", "logs", "status", "doctor", "feishu"])
    parser.add_argument("subcommand", nargs="*", help="子命令和参数")
    args = parser.parse_args()
    
    host = args.host
    
    if args.command == "models":
        if not args.subcommand:
            print("用法: models [list|status|set <model-id>]")
            sys.exit(1)
        sub = args.subcommand[0]
        if sub == "list":
            print(run_remote_command(host, "openclaw models list"))
        elif sub == "status":
            print(run_remote_command(host, "openclaw models status"))
        elif sub == "set" and len(args.subcommand) > 1:
            model = args.subcommand[1]
            print(run_remote_command(host, f"openclaw models set {model}"))
            print(f"\n[提示] 模型已设置为 {model}，需要重启Gateway生效")
        else:
            print("用法: models set <model-id>")
            
    elif args.command == "config":
        if not args.subcommand:
            print("用法: config [get <path>|set <path> <value>]")
            sys.exit(1)
        sub = args.subcommand[0]
        if sub == "get" and len(args.subcommand) > 1:
            path = args.subcommand[1]
            print(run_remote_command(host, f"openclaw config get {path}"))
        elif sub == "set" and len(args.subcommand) > 2:
            path = args.subcommand[1]
            value = " ".join(args.subcommand[2:])
            print(run_remote_command(host, f"openclaw config set {path} {value}"))
        else:
            print("用法: config get <path> | config set <path> <value>")
            
    elif args.command == "gateway":
        if not args.subcommand or args.subcommand[0] != "restart":
            print("用法: gateway restart")
            sys.exit(1)
        print("正在重启Gateway...")
        print(run_remote_command(host, "pkill -9 -f openclaw; sleep 2; nohup openclaw gateway run --force > /dev/null 2>&1 &"))
        print("Gateway已启动")
        
    elif args.command == "logs":
        lines = 50
        if args.subcommand and args.subcommand[0].isdigit():
            lines = args.subcommand[0]
        print(run_remote_command(host, f"tail -{lines} /tmp/openclaw/openclaw-*.log"))
        
    elif args.command == "status":
        print(run_remote_command(host, "openclaw status"))
        
    elif args.command == "doctor":
        print(run_remote_command(host, "openclaw doctor"))
        
    elif args.command == "feishu":
        if not args.subcommand:
            print("用法: feishu [websocket|dm <policy>]")
            sys.exit(1)
        sub = args.subcommand[0]
        if sub == "websocket":
            print(run_remote_command(host, "openclaw config set channels.feishu.use_websocket true"))
            print("已启用WebSocket模式，需要重启Gateway生效")
        elif sub == "dm" and len(args.subcommand) > 1:
            policy = args.subcommand[1]
            print(run_remote_command(host, f"openclaw config set channels.feishu.dmPolicy {policy}"))
            print(f"已设置dmPolicy为 {policy}，需要重启Gateway生效")
        else:
            print("用法: feishu websocket | feishu dm <anyone|pairing>")

if __name__ == "__main__":
    main()
