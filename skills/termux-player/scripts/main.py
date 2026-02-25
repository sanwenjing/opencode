# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import argparse
import subprocess
import json

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(SKILL_DIR, "config", "config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"default_host": "termux", "music_dir": "/sdcard/Download/music"}

def get_remote_manager_script():
    rm_dir = os.path.join(os.path.dirname(SKILL_DIR), "remote-manager", "scripts", "main.py")
    if os.path.exists(rm_dir):
        return rm_dir
    return "/root/.config/opencode/skills/remote-manager/scripts/main.py"

def exec_on_host(host_name, command):
    rm_script = get_remote_manager_script()
    result = subprocess.run(
        ["python3", rm_script, "exec", "-c", command, "-n", host_name],
        capture_output=True,
        text=True,
        cwd=os.getcwd()
    )
    output = result.stdout
    lines = output.split('\n')
    valid_lines = []
    in_section = False
    capture = False
    for line in lines:
        if '--------' in line:
            if not in_section:
                in_section = True
                capture = True
            else:
                capture = False
            continue
        if capture and line.strip() and not line.startswith('[') and '执行' not in line and '=' not in line and '/' in line:
            valid_lines.append(line.strip())
    return '\n'.join(valid_lines), result.stderr

def list_music_files(host_name, music_dir):
    stdout, _ = exec_on_host(host_name, f'find "{music_dir}" -name "*.mp3" -o -name "*.m4a" -o -name "*.wav" 2>/dev/null')
    files = [f.strip() for f in stdout.split('\n') if f.strip() and f.strip().endswith(('.mp3', '.m4a', '.wav'))]
    return files

def play(host_name, file_path):
    stdout, stderr = exec_on_host(host_name, f'termux-media-player play "{file_path}" 2>&1')
    if "Now Playing" in stdout or not stderr:
        print(f"正在播放: {os.path.basename(file_path)}")
        return True
    print(f"播放失败: {stderr or stdout}")
    return False

def pause(host_name):
    exec_on_host(host_name, 'termux-media-player pause 2>&1')
    print("已暂停")

def resume(host_name):
    exec_on_host(host_name, 'termux-media-player play 2>&1')
    print("继续播放")

def stop(host_name):
    exec_on_host(host_name, 'termux-media-player stop 2>&1')
    print("已停止")

def info(host_name):
    stdout, _ = exec_on_host(host_name, 'termux-media-player info 2>&1')
    print(stdout or "无播放信息")

def main():
    config = load_config()
    default_host = config.get("default_host", "termux")
    music_dir = config.get("music_dir", "/sdcard/Download/music")

    parser = argparse.ArgumentParser(description='Termux音乐播放器')
    parser.add_argument('command', choices=['play', 'pause', 'resume', 'stop', 'info', 'list'], help='播放命令')
    parser.add_argument('file', nargs='?', help='播放文件路径(play命令需要)')
    parser.add_argument('--host', '-n', default=default_host, help='远程主机名')
    parser.add_argument('--dir', '-d', default=music_dir, help='音乐目录路径')
    args = parser.parse_args()

    host = args.host
    cmd = args.command
    music_dir = args.dir

    if cmd == 'list':
        files = list_music_files(host, music_dir)
        print(f"音乐目录: {music_dir}")
        print(f"可用音乐 ({len(files)}首):")
        for i, f in enumerate(files, 1):
            print(f"  {i}. {os.path.basename(f)}")
        return

    if cmd == 'play':
        if not args.file:
            print("请指定播放文件路径")
            return
        full_path = args.file if args.file.startswith('/') else os.path.join(music_dir, args.file)
        play(host, full_path)
    elif cmd == 'pause':
        pause(host)
    elif cmd == 'resume':
        resume(host)
    elif cmd == 'stop':
        stop(host)
    elif cmd == 'info':
        info(host)

if __name__ == '__main__':
    main()
