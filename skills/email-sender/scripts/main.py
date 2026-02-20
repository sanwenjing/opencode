# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import json
import smtplib
import argparse
import zipfile
import shutil
import tempfile
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from pathlib import Path

PATH_SEP = os.sep


def get_output_path(filename: str) -> str:
    """获取输出文件的完整路径"""
    return os.path.join(os.getcwd(), filename)


def get_config_path() -> str:
    """获取配置文件路径"""
    return get_output_path("email_sender_config.json")


def create_default_config():
    """创建默认配置文件"""
    config = {
        "smtp_server": "smtp.example.com",
        "smtp_port": 465,
        "use_ssl": True,
        "username": "your_email@example.com",
        "password": "your_password",
        "from_name": "Email Sender",
        "default_to": "",
        "auto_subject_prefix": "[自动邮件]",
        "subject_date_format": "%Y-%m-%d %H:%M"
    }
    
    config_path = get_config_path()
    if not os.path.exists(config_path):
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        print(f"配置文件已创建: {config_path}")
        print("请编辑配置文件添加您的邮件账号信息")
    return config


def load_config() -> dict:
    """加载配置文件"""
    config_path = get_config_path()
    if not os.path.exists(config_path):
        return create_default_config()
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    username = config.get('username', '')
    from_name = config.get('from_name', '')
    
    if not from_name or from_name == username:
        if '@' in username:
            config['from_name'] = username.split('@')[0]
        else:
            config['from_name'] = username
    
    return config


def generate_auto_subject(prefix: str = "", date_format: str = "%Y-%m-%d %H:%M") -> str:
    """自动生成邮件主题"""
    timestamp = datetime.now().strftime(date_format)
    if prefix:
        return f"{prefix} {timestamp}"
    return f"邮件 {timestamp}"


def pack_folder(folder_path: str) -> str:
    """将文件夹打包成zip文件"""
    if not os.path.isdir(folder_path):
        raise ValueError(f"目录不存在: {folder_path}")
    
    folder_name = os.path.basename(os.path.normpath(folder_path))
    zip_path = get_output_path(f"{folder_name}.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(folder_path))
                zipf.write(file_path, arcname)
    
    return zip_path


def send_email(to_addr: str, subject: str = None, body: str = "", 
               attachments: list = None, config: dict = None):
    """发送邮件"""
    if config is None:
        config = load_config()
    
    if attachments is None:
        attachments = []
    
    msg = MIMEMultipart()
    msg['From'] = f"{config.get('from_name', '')} <{config['username']}>"
    msg['To'] = to_addr
    
    if subject is None:
        subject = generate_auto_subject(
            config.get('auto_subject_prefix', ''),
            config.get('subject_date_format', '%Y-%m-%d %H:%M')
        )
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    for attachment_path in attachments:
        if not os.path.exists(attachment_path):
            print(f"警告: 附件不存在: {attachment_path}")
            continue
        
        filename = os.path.basename(attachment_path)
        with open(attachment_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {filename}')
        msg.attach(part)
    
    smtp_server = config['smtp_server']
    smtp_port = config['smtp_port']
    use_ssl = config.get('use_ssl', True)
    username = config['username']
    password = config['password']
    
    try:
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
        
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        
        print(f"邮件发送成功!")
        print(f"收件人: {to_addr}")
        print(f"主题: {subject}")
        if attachments:
            print(f"附件: {', '.join([os.path.basename(a) for a in attachments])}")
        
        save_send_log(to_addr, subject, body, True)
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"邮件发送失败: {error_msg}")
        save_send_log(to_addr, subject, body, False, error_msg)
        return False


def handle_attachments(attachment_args: list) -> list:
    """处理附件参数，支持文件和文件夹"""
    attachments = []
    temp_files = []
    
    for arg in attachment_args:
        if os.path.isdir(arg):
            print(f"打包文件夹: {arg}")
            zip_path = pack_folder(arg)
            attachments.append(zip_path)
            temp_files.append(zip_path)
        elif os.path.isfile(arg):
            attachments.append(arg)
        else:
            print(f"警告: 文件不存在: {arg}")
    
    return attachments, temp_files


def cleanup_temp_files(temp_files: list):
    """清理临时文件"""
    for f in temp_files:
        try:
            os.remove(f)
            print(f"已清理临时文件: {f}")
        except Exception as e:
            print(f"清理失败: {f} - {str(e)}")


def get_log_path() -> str:
    """获取日志文件路径"""
    return get_output_path("email_send_log.json")


def save_send_log(to_addr: str, subject: str, body: str, success: bool, error_msg: str = ""):
    """保存发送日志"""
    log_path = get_log_path()
    log_entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "to": to_addr,
        "subject": subject,
        "body": body[:200] + "..." if len(body) > 200 else body,
        "success": success,
        "error": error_msg
    }
    
    logs = []
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except:
            logs = []
    
    logs.append(log_entry)
    
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    
    print(f"日志已保存: {log_path}")


def main():
    parser = argparse.ArgumentParser(description='邮件发送工具')
    parser.add_argument('--to', '-t', help='收件人邮箱')
    parser.add_argument('--subject', '-s', help='邮件主题（留空则自动生成）')
    parser.add_argument('--body', '-b', help='邮件正文', default='')
    parser.add_argument('--body-file', '-f', help='邮件正文文件路径')
    parser.add_argument('--attachment', '-a', help='附件文件或文件夹（可多次使用）', action='append')
    parser.add_argument('--config', '-c', help='配置文件路径（默认: email_sender_config.json）')
    parser.add_argument('--init-config', '-i', action='store_true', help='创建默认配置文件')
    parser.add_argument('--yes', '-y', action='store_true', help='跳过确认直接发送邮件')
    
    args = parser.parse_args()
    
    if args.init_config:
        create_default_config()
        return
    
    config = load_config()
    
    if not args.to:
        default_to = config.get('default_to', '')
        if not default_to:
            parser.error('--to is required unless using --init-config or配置 default_to')
        args.to = default_to
    
    if args.config:
        global config_path
        config_path = args.config
        config = load_config()
    
    if not config.get('username') or config.get('username') == 'your_email@example.com':
        print("错误: 请先配置邮件账号信息")
        print(f"请编辑配置文件: {get_config_path()}")
        create_default_config()
        return
    
    body = args.body
    if args.body_file:
        if os.path.exists(args.body_file):
            with open(args.body_file, 'r', encoding='utf-8') as f:
                body = f.read()
        else:
            print(f"错误: 文件不存在: {args.body_file}")
            return
    
    attachments = []
    temp_files = []
    if args.attachment:
        attachments, temp_files = handle_attachments(args.attachment)
    
    print(f"\n收件人: {args.to}")
    print(f"主题: {args.subject or '自动生成'}")
    print(f"正文: {body[:50] + '...' if len(body) > 50 else body or '(无)'}")
    if attachments:
        print(f"附件: {', '.join([os.path.basename(a) for a in attachments])}")
    
    if not args.yes:
        confirm = input("\n确认发送? (y/n): ").strip().lower()
        if confirm != 'y' and confirm != 'yes':
            print("已取消发送")
            cleanup_temp_files(temp_files)
            return
    
    try:
        success = send_email(
            to_addr=args.to,
            subject=args.subject,
            body=body,
            attachments=attachments,
            config=config
        )
        
        if success:
            print("\n邮件发送完成!")
        else:
            print("\n邮件发送失败，请检查配置")
            
    finally:
        cleanup_temp_files(temp_files)


if __name__ == '__main__':
    main()
