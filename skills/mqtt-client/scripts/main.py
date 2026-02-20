# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import json
import argparse
import time
import ssl
from typing import Optional

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion


PATH_SEP = os.sep


def get_skill_dir() -> str:
    """获取技能目录"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_config_path() -> str:
    """获取配置文件路径"""
    skill_dir = get_skill_dir()
    return os.path.join(skill_dir, "config", "mqtt_config.json")


def load_config(config_file: Optional[str] = None) -> dict:
    """加载配置文件"""
    if config_file:
        config_path = config_file
    else:
        config_path = get_config_path()
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_config(config: dict, config_file: Optional[str] = None):
    """保存配置文件"""
    if config_file:
        config_path = config_file
    else:
        config_path = get_config_path()
    
    config_dir = os.path.dirname(config_path)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"配置已保存到: {config_path}")


def create_client(config: dict) -> mqtt.Client:
    """创建 MQTT 客户端"""
    client_id = config.get('client_id', f'mqtt-client-{int(time.time())}')
    client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2, client_id=client_id)
    
    if config.get('username'):
        client.username_pw_set(config['username'], config.get('password', ''))
    
    if config.get('use_tls', False):
        client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
        if config.get('tls_insecure', False):
            client.tls_insecure_set(True)
    
    return client


def on_connect(client, userdata, flags, reason_code, properties):
    """连接回调"""
    if reason_code == 0:
        print("[连接] 成功连接到 Broker")
        subscribe_topics = userdata.get('subscribe', [])
        for topic in subscribe_topics:
            qos = userdata.get('qos', 0)
            client.subscribe(topic, qos=qos)
            print(f"[订阅] 主题: {topic}, QoS: {qos}")
    else:
        print(f"[连接] 失败，原因码: {reason_code}")


def on_message(client, userdata, msg):
    """消息回调"""
    topic = msg.topic
    payload = msg.payload.decode('utf-8', errors='ignore')
    print(f"[消息] 主题: {topic}")
    print(f"[消息] 内容: {payload}")
    
    if userdata.get('save_messages', False):
        output_file = userdata.get('output_file', 'mqtt_messages.txt')
        output_path = os.path.join(os.getcwd(), output_file)
        with open(output_path, 'a', encoding='utf-8') as f:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] {topic}: {payload}\n")


def on_disconnect(client, userdata, reason_code, properties):
    """断开连接回调"""
    print(f"[断开] 已断开连接，原因码: {reason_code}")


def on_subscribe(client, userdata, mid, reason_codes, properties):
    """订阅回调"""
    print(f"[订阅] 订阅成功，mid: {mid}")


def on_publish(client, userdata, mid, reason_code, properties):
    """发布回调"""
    print(f"[发布] 消息已发布，mid: {mid}")


def cmd_connect(args):
    """连接到 Broker 并保持连接"""
    config = load_config(args.config)
    
    if args.host:
        config['host'] = args.host
    if args.port:
        config['port'] = args.port
    if args.username:
        config['username'] = args.username
    if args.password:
        config['password'] = args.password
    if args.tls:
        config['use_tls'] = True
    if args.client_id:
        config['client_id'] = args.client_id
    
    host = config.get('host', 'localhost')
    port = config.get('port', 1883)
    keepalive = config.get('keepalive', 60)
    
    userdata = {
        'save_messages': args.save,
        'output_file': args.output,
        'qos': args.qos,
        'subscribe': args.subscribe if args.subscribe else []
    }
    
    client = create_client(config)
    client.user_data_set(userdata)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe
    client.on_publish = on_publish
    
    print(f"[连接] 正在连接 {host}:{port}...")
    
    try:
        client.connect(host, port, keepalive)
    except Exception as e:
        print(f"[错误] 连接失败: {e}")
        return 1
    
    if args.subscribe:
        print(f"[订阅] 将在连接后订阅: {', '.join(args.subscribe)}")
    
    print("[提示] 按 Ctrl+C 断开连接")
    
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n[断开] 用户中断，正在断开连接...")
        client.disconnect()
    
    return 0


def cmd_publish(args):
    """发布消息"""
    config = load_config(args.config)
    
    if args.host:
        config['host'] = args.host
    if args.port:
        config['port'] = args.port
    if args.username:
        config['username'] = args.username
    if args.password:
        config['password'] = args.password
    if args.tls:
        config['use_tls'] = True
    
    host = config.get('host', 'localhost')
    port = config.get('port', 1883)
    keepalive = config.get('keepalive', 60)
    
    client = create_client(config)
    client.on_publish = on_publish
    
    print(f"[连接] 正在连接 {host}:{port}...")
    
    try:
        client.connect(host, port, keepalive)
    except Exception as e:
        print(f"[错误] 连接失败: {e}")
        return 1
    
    client.loop_start()
    
    try:
        result = client.publish(args.topic, args.message, qos=args.qos, retain=args.retain)
        result.wait_for_publish(timeout=5)
        print(f"[发布] 主题: {args.topic}")
        print(f"[发布] 内容: {args.message}")
        print(f"[发布] QoS: {args.qos}, Retain: {args.retain}")
    except Exception as e:
        print(f"[错误] 发布失败: {e}")
        return 1
    finally:
        client.loop_stop()
        client.disconnect()
    
    return 0


def cmd_subscribe(args):
    """订阅主题"""
    config = load_config(args.config)
    
    if args.host:
        config['host'] = args.host
    if args.port:
        config['port'] = args.port
    if args.username:
        config['username'] = args.username
    if args.password:
        config['password'] = args.password
    if args.tls:
        config['use_tls'] = True
    
    host = config.get('host', 'localhost')
    port = config.get('port', 1883)
    keepalive = config.get('keepalive', 60)
    
    userdata = {
        'save_messages': args.save,
        'output_file': args.output,
        'qos': args.qos,
        'subscribe': [args.topic]
    }
    
    client = create_client(config)
    client.user_data_set(userdata)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe
    
    print(f"[连接] 正在连接 {host}:{port}...")
    
    try:
        client.connect(host, port, keepalive)
    except Exception as e:
        print(f"[错误] 连接失败: {e}")
        return 1
    
    print(f"[订阅] 主题: {args.topic}, QoS: {args.qos}")
    print("[提示] 按 Ctrl+C 取消订阅")
    
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n[断开] 用户中断，正在断开连接...")
        client.disconnect()
    
    return 0


def cmd_config(args):
    """配置管理"""
    if args.show:
        config = load_config(args.config)
        print("当前配置:")
        print(json.dumps(config, indent=2, ensure_ascii=False))
        return 0
    
    config = load_config(args.config)
    
    if args.set_host:
        config['host'] = args.set_host
    if args.set_port:
        config['port'] = args.set_port
    if args.set_username:
        config['username'] = args.set_username
    if args.set_password:
        config['password'] = args.set_password
    if args.set_tls:
        config['use_tls'] = args.set_tls.lower() in ('true', '1', 'yes')
    if args.set_client_id:
        config['client_id'] = args.set_client_id
    if args.set_keepalive:
        config['keepalive'] = args.set_keepalive
    
    save_config(config, args.config)
    return 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='MQTT 客户端工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 设置配置
  python main.py config --set-host broker.emqx.io --set-port 1883
  
  # 发布消息
  python main.py pub -t test/topic -m "Hello MQTT"
  
  # 订阅主题
  python main.py sub -t test/topic
  
  # 连接并订阅多个主题
  python main.py connect -s test/topic1 -s test/topic2
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # config 命令
    config_parser = subparsers.add_parser('config', help='配置管理')
    config_parser.add_argument('--config', '-c', help='配置文件路径')
    config_parser.add_argument('--show', action='store_true', help='显示当前配置')
    config_parser.add_argument('--set-host', help='设置 Broker 地址')
    config_parser.add_argument('--set-port', type=int, help='设置 Broker 端口')
    config_parser.add_argument('--set-username', help='设置用户名')
    config_parser.add_argument('--set-password', help='设置密码')
    config_parser.add_argument('--set-tls', help='启用 TLS (true/false)')
    config_parser.add_argument('--set-client-id', help='设置客户端 ID')
    config_parser.add_argument('--set-keepalive', type=int, help='设置保活时间(秒)')
    
    # publish 命令
    pub_parser = subparsers.add_parser('pub', help='发布消息')
    pub_parser.add_argument('--config', '-c', help='配置文件路径')
    pub_parser.add_argument('--host', '-H', help='Broker 地址')
    pub_parser.add_argument('--port', '-p', type=int, help='Broker 端口')
    pub_parser.add_argument('--username', '-u', help='用户名')
    pub_parser.add_argument('--password', '-P', help='密码')
    pub_parser.add_argument('--tls', action='store_true', help='启用 TLS')
    pub_parser.add_argument('--topic', '-t', required=True, help='消息主题')
    pub_parser.add_argument('--message', '-m', required=True, help='消息内容')
    pub_parser.add_argument('--qos', '-q', type=int, default=0, choices=[0, 1, 2], help='QoS 等级')
    pub_parser.add_argument('--retain', '-r', action='store_true', help='保留消息')
    
    # subscribe 命令
    sub_parser = subparsers.add_parser('sub', help='订阅主题')
    sub_parser.add_argument('--config', '-c', help='配置文件路径')
    sub_parser.add_argument('--host', '-H', help='Broker 地址')
    sub_parser.add_argument('--port', '-p', type=int, help='Broker 端口')
    sub_parser.add_argument('--username', '-u', help='用户名')
    sub_parser.add_argument('--password', '-P', help='密码')
    sub_parser.add_argument('--tls', action='store_true', help='启用 TLS')
    sub_parser.add_argument('--topic', '-t', required=True, help='订阅主题')
    sub_parser.add_argument('--qos', '-q', type=int, default=0, choices=[0, 1, 2], help='QoS 等级')
    sub_parser.add_argument('--save', '-s', action='store_true', help='保存消息到文件')
    sub_parser.add_argument('--output', '-o', default='mqtt_messages.txt', help='输出文件名')
    
    # connect 命令
    conn_parser = subparsers.add_parser('connect', help='连接到 Broker')
    conn_parser.add_argument('--config', '-c', help='配置文件路径')
    conn_parser.add_argument('--host', '-H', help='Broker 地址')
    conn_parser.add_argument('--port', '-p', type=int, help='Broker 端口')
    conn_parser.add_argument('--username', '-u', help='用户名')
    conn_parser.add_argument('--password', '-P', help='密码')
    conn_parser.add_argument('--tls', action='store_true', help='启用 TLS')
    conn_parser.add_argument('--client-id', help='客户端 ID')
    conn_parser.add_argument('--subscribe', '-s', action='append', help='订阅主题(可多次使用)')
    conn_parser.add_argument('--qos', '-q', type=int, default=0, choices=[0, 1, 2], help='QoS 等级')
    conn_parser.add_argument('--save', action='store_true', help='保存消息到文件')
    conn_parser.add_argument('--output', '-o', default='mqtt_messages.txt', help='输出文件名')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        'config': cmd_config,
        'pub': cmd_publish,
        'sub': cmd_subscribe,
        'connect': cmd_connect,
    }
    
    return commands[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
