# -*- coding: utf-8 -*-
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import argparse
import subprocess

REMOTE_MANAGER_PATH = os.path.join(
    os.path.expanduser("~"), ".config", "opencode", "skills", "remote-manager", "scripts", "main.py"
)

TERMUX_APIS = {
    "battery-status": {"cmd": "termux-battery-status", "desc": "获取电池状态"},
    "brightness": {"cmd": "termux-brightness", "desc": "设置屏幕亮度", "args": True},
    "vibrate": {"cmd": "termux-vibrate", "desc": "设备振动", "args": True},
    "torch": {"cmd": "termux-torch", "desc": "手电筒开关", "args": True},
    "volume": {"cmd": "termux-volume", "desc": "音量控制", "args": True},
    "wake-lock": {"cmd": "termux-wake-lock", "desc": "保持唤醒"},
    "wake-unlock": {"cmd": "termux-wake-unlock", "desc": "释放唤醒"},
    "info": {"cmd": "termux-info", "desc": "设备信息"},
    
    "sms-send": {"cmd": "termux-sms-send", "desc": "发送短信", "args": True},
    "sms-list": {"cmd": "termux-sms-list", "desc": "短信列表", "args": True},
    "call-log": {"cmd": "termux-call-log", "desc": "通话记录", "args": True},
    "telephony-call": {"cmd": "termux-telephony-call", "desc": "拨打电话", "args": True},
    "telephony-deviceinfo": {"cmd": "termux-telephony-deviceinfo", "desc": "电话设备信息"},
    "telephony-cellinfo": {"cmd": "termux-telephony-cellinfo", "desc": "基站信息"},
    
    "location": {"cmd": "termux-location", "desc": "GPS位置", "args": True},
    "sensor": {"cmd": "termux-sensor", "desc": "传感器数据", "args": True},
    "infrared-frequencies": {"cmd": "termux-infrared-frequencies", "desc": "红外频率"},
    "infrared-transmit": {"cmd": "termux-infrared-transmit", "desc": "发射红外", "args": True},
    
    "camera-info": {"cmd": "termux-camera-info", "desc": "相机信息"},
    "camera-photo": {"cmd": "termux-camera-photo", "desc": "拍照", "args": True},
    "microphone-record": {"cmd": "termux-microphone-record", "desc": "录音", "args": True},
    "media-player": {"cmd": "termux-media-player", "desc": "播放媒体", "args": True},
    "audio-info": {"cmd": "termux-audio-info", "desc": "音频信息"},
    
    "clipboard-get": {"cmd": "termux-clipboard-get", "desc": "获取剪贴板"},
    "clipboard-set": {"cmd": "termux-clipboard-set", "desc": "设置剪贴板", "args": True},
    "notification": {"cmd": "termux-notification", "desc": "发送通知", "args": True},
    "notification-list": {"cmd": "termux-notification-list", "desc": "通知列表"},
    "notification-remove": {"cmd": "termux-notification-remove", "desc": "移除通知", "args": True},
    "toast": {"cmd": "termux-toast", "desc": "弹出提示", "args": True},
    
    "wifi-connectioninfo": {"cmd": "termux-wifi-connectioninfo", "desc": "WiFi信息"},
    "wifi-enable": {"cmd": "termux-wifi-enable", "desc": "WiFi开关", "args": True},
    "wifi-scaninfo": {"cmd": "termux-wifi-scaninfo", "desc": "WiFi扫描"},
    
    "dialog": {"cmd": "termux-dialog", "desc": "对话框", "args": True},
    "fingerprint": {"cmd": "termux-fingerprint", "desc": "指纹识别"},
    "speech-to-text": {"cmd": "termux-speech-to-text", "desc": "语音转文字"},
    "tts-engines": {"cmd": "termux-tts-engines", "desc": "TTS引擎列表"},
    "tts-speak": {"cmd": "termux-tts-speak", "desc": "文字转语音", "args": True},
    
    "contact-list": {"cmd": "termux-contact-list", "desc": "联系人列表"},
    "share": {"cmd": "termux-share", "desc": "分享文件", "args": True},
    "download": {"cmd": "termux-download", "desc": "下载文件", "args": True},
    "wallpaper": {"cmd": "termux-wallpaper", "desc": "更换壁纸", "args": True},
    
    "usb": {"cmd": "termux-usb", "desc": "USB设备", "args": True},
    "job-scheduler": {"cmd": "termux-job-scheduler", "desc": "计划任务", "args": True},
    "open": {"cmd": "termux-open", "desc": "打开文件/URL", "args": True},
    "open-url": {"cmd": "termux-open-url", "desc": "打开URL", "args": True},
}


def exec_on_remote(command, host="termux"):
    if not os.path.exists(REMOTE_MANAGER_PATH):
        print(f"错误: remote-manager 技能不存在: {REMOTE_MANAGER_PATH}")
        return None
    
    result = subprocess.run(
        [sys.executable, REMOTE_MANAGER_PATH, "exec", "-c", command, "-n", host],
        capture_output=True,
        text=True
    )
    return result


def list_apis():
    print("可用 Termux API 命令:")
    print("-" * 50)
    print(f"{'命令':<25} {'描述'}")
    print("-" * 50)
    for name, info in sorted(TERMUX_APIS.items()):
        print(f"{name:<25} {info['desc']}")
    print("-" * 50)


def exec_api(api_name, args=None, host="termux"):
    if api_name not in TERMUX_APIS:
        print(f"错误: 未知 API: {api_name}")
        print("使用 'list' 命令查看可用 API")
        return False
    
    api_info = TERMUX_APIS[api_name]
    cmd = api_info["cmd"]
    
    if args:
        full_cmd = f"{cmd} {args}"
    else:
        full_cmd = cmd
    
    print(f"执行: {full_cmd}")
    result = exec_on_remote(full_cmd, host)
    
    if result and result.returncode == 0:
        print(result.stdout)
        return True
    else:
        if result:
            print(f"执行失败: {result.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Termux API 控制器")
    parser.add_argument("command", nargs="?", help="命令: list, <api-name>")
    parser.add_argument("args", nargs="?", help="API 参数")
    parser.add_argument("--host", "-n", default="termux", help="远程主机名 (默认: termux)")
    
    args = parser.parse_args()
    
    if args.command == "list" or args.command is None:
        list_apis()
    else:
        exec_api(args.command, args.args, args.host)


if __name__ == "__main__":
    main()
