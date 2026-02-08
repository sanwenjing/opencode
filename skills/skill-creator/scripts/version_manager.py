# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import yaml
import argparse
import semver
from datetime import datetime
from typing import Optional

SKILLS_DIR = r"C:\Users\Administrator\.config\opencode\skills"


def get_skill_path(skill_name: str) -> str:
    """获取技能目录路径"""
    return os.path.join(SKILLS_DIR, skill_name)


def read_skill_md(skill_path: str) -> Optional[dict]:
    """读取SKILL.md的front matter"""
    skill_md_path = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md_path):
        return None
    
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 2:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                    return frontmatter
                except:
                    return None
    return None


def update_version(skill_name: str, version: str, message: str) -> bool:
    """更新技能版本并记录日志"""
    skill_path = get_skill_path(skill_name)
    
    if not os.path.exists(skill_path):
        print(f"错误: 技能 '{skill_name}' 不存在")
        return False
    
    # 验证版本格式
    if not semver.VersionInfo.is_valid(version):
        print(f"错误: 无效的版本号 '{version}'，请使用 MAJOR.MINOR.PATCH 格式")
        return False
    
    # 更新SKILL.md
    skill_md_path = os.path.join(skill_path, "SKILL.md")
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    old_version = "0.0.0"
    
    # 更新front matter中的版本
    if content.startswith('---'):
        parts = content.split('---', 2)
        try:
            frontmatter = yaml.safe_load(parts[1])
            old_version = frontmatter.get('version', '0.0.0')
            frontmatter['version'] = version
            
            new_frontmatter = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
            new_content = f"---\n{new_frontmatter}---{parts[2] if len(parts) > 2 else ''}"
            
            with open(skill_md_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        except Exception as e:
            print(f"错误: 更新SKILL.md失败: {e}")
            return False
    
    # 更新CHANGELOG.md
    changelog_path = os.path.join(skill_path, "CHANGELOG.md")
    
    # 解析变更类型
    change_type = "Changed"
    msg_lower = message.lower()
    if any(word in msg_lower for word in ['新增', 'added', 'add', '新功能']):
        change_type = "Added"
    elif any(word in msg_lower for word in ['修复', 'fixed', 'fix', 'bug']):
        change_type = "Fixed"
    elif any(word in msg_lower for word in ['删除', 'removed', 'remove', '移除']):
        change_type = "Removed"
    elif any(word in msg_lower for word in ['废弃', 'deprecated', 'deprecate']):
        change_type = "Deprecated"
    
    # 格式化消息（支持中英文）
    formatted_message = message.strip()
    
    changelog_entry = f"""## [{version}] - {datetime.now().strftime('%Y-%m-%d')}

### {change_type}
- {formatted_message}

"""
    
    if os.path.exists(changelog_path):
        with open(changelog_path, 'r', encoding='utf-8') as f:
            changelog_content = f.read()
        
        # 找到第一个 ## [ 版本行，插入到它之前
        lines = changelog_content.split('\n')
        new_lines = []
        inserted = False
        for i, line in enumerate(lines):
            if line.startswith('## ['):
                # 在这里插入新条目
                new_lines.append(changelog_entry.rstrip())
                inserted = True
            new_lines.append(line)
        
        if not inserted:
            new_lines.insert(0, changelog_entry.rstrip())
        
        changelog_content = '\n'.join(new_lines)
    else:
        # 创建新的CHANGELOG.md
        changelog_content = f"""# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

{changelog_entry}
"""
    
    with open(changelog_path, 'w', encoding='utf-8') as f:
        f.write(changelog_content)
    
    print(f"✓ 版本已更新: {old_version} → {version}")
    print(f"✓ 变更日志已记录: {message}")
    return True


def bump_version(skill_name: str, bump_type: str, message: str) -> bool:
    """自动递增版本号"""
    skill_path = get_skill_path(skill_name)
    
    frontmatter = read_skill_md(skill_path)
    if not frontmatter:
        print(f"错误: 无法读取技能 '{skill_name}'")
        return False
    
    current_version = frontmatter.get('version', '0.0.0')
    ver = semver.VersionInfo.parse(current_version)
    
    if bump_type == 'major':
        new_version = ver.bump_major()
    elif bump_type == 'minor':
        new_version = ver.bump_minor()
    else:  # patch
        new_version = ver.bump_patch()
    
    return update_version(skill_name, str(new_version), message)


def show_info(skill_name: str) -> None:
    """显示技能版本信息"""
    skill_path = get_skill_path(skill_name)
    
    if not os.path.exists(skill_path):
        print(f"错误: 技能 '{skill_name}' 不存在")
        return
    
    frontmatter = read_skill_md(skill_path)
    if frontmatter:
        print(f"\n技能: {skill_name}")
        print(f"  版本: {frontmatter.get('version', '未设置')}")
        print(f"  描述: {frontmatter.get('description', '无')}")
    else:
        print(f"无法读取技能信息")


def show_changelog(skill_name: str) -> None:
    """显示技能变更日志"""
    skill_path = get_skill_path(skill_name)
    changelog_path = os.path.join(skill_path, "CHANGELOG.md")
    
    if not os.path.exists(changelog_path):
        print(f"错误: CHANGELOG.md 不存在")
        return
    
    with open(changelog_path, 'r', encoding='utf-8') as f:
        print(f.read())


def main():
    parser = argparse.ArgumentParser(
        description='技能版本管理工具 - 更新版本号和变更日志',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 设置特定版本
  python scripts/version_manager.py --skill my-skill --version 1.1.0 --message "新增批量执行功能"

  # 递增版本号（补丁）
  python scripts/version_manager.py --skill my-skill --bump patch --message "修复bug"

  # 递增版本号（次要）
  python scripts/version_manager.py --skill my-skill --bump minor --message "新增功能"

  # 递增版本号（主要）
  python scripts/version_manager.py --skill my-skill --bump major --message "重构API"

  # 查看版本信息
  python scripts/version_manager.py --skill my-skill --info

  # 查看变更日志
  python scripts/version_manager.py --skill my-skill --changelog
        """
    )

    parser.add_argument('--skill', '-s', required=True, help='技能名称')
    parser.add_argument('--version', '-v', help='指定版本号 (格式: MAJOR.MINOR.PATCH)')
    parser.add_argument('--bump', choices=['major', 'minor', 'patch'], help='自动递增版本号')
    parser.add_argument('--message', '-m', help='变更日志消息（更新版本时必需）')
    parser.add_argument('--info', action='store_true', help='显示技能版本信息')
    parser.add_argument('--changelog', action='store_true', help='显示变更日志')

    args = parser.parse_args()

    if args.info:
        show_info(args.skill)
    elif args.changelog:
        show_changelog(args.skill)
    elif args.version:
        if not args.message:
            print("错误: 更新版本时必须指定 --message 参数")
            return
        if update_version(args.skill, args.version, args.message):
            print(f"\n完成！技能 '{args.skill}' 已更新到版本 {args.version}")
    elif args.bump:
        if not args.message:
            print("错误: 递增版本时必须指定 --message 参数")
            return
        if bump_version(args.skill, args.bump, args.message):
            print(f"\n完成！技能 '{args.skill}' 版本已递增")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
