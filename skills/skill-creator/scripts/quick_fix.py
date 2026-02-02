# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

#!/usr/bin/env python3
"""
快速技能修复脚本 (Quick Skill Fix)

快速修复常见技能问题的简化工具
"""

import os
import sys
import re
from pathlib import Path

def fix_yaml_frontmatter(skill_dir: str) -> bool:
    """为技能添加 YAML front matter"""
    skill_name = os.path.basename(skill_dir)
    skill_md = os.path.join(skill_dir, 'SKILL.md')
    
    if not os.path.exists(skill_md):
        return False
    
    try:
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已有 YAML front matter
        if content.startswith('---\n'):
            return True  # 已经有了
        
        # 提取现有标题作为描述
        first_line = content.split('\n')[0] if content else f"# {skill_name}"
        title = first_line.replace('#', '').strip()
        
        # 生成 YAML front matter
        yaml_block = f"""---
name: {skill_name}
description: "{title} - 专业的技能工具，用于..."
license: 专有。LICENSE.txt 包含完整条款
---

"""
        
        # 写入文件
        with open(skill_md, 'w', encoding='utf-8') as f:
            f.write(yaml_block + content)
        
        # 使用系统路径分隔符显示路径
        display_path = os.path.normpath(skill_md)
        print(f"修复了技能 {skill_name} 的 YAML front matter")
        print(f"文件位置: {display_path}")
        return True
        
    except Exception as e:
        print(f"修复 {skill_name} 时出错: {str(e)}")
        return False

def scan_and_fix_skills(skills_dir: str = ""):
    """扫描并修复所有技能"""
    if not skills_dir:
        skills_dir = os.path.join(os.path.dirname(__file__), "..", "..")
    
    fixed_count = 0
    total_count = 0
    
    print("扫描技能目录...")
    
    for item in os.listdir(skills_dir):
        item_path = os.path.join(skills_dir, item)
        
        if os.path.isdir(item_path) and not item.startswith('.') and item != 'node_modules':
            skill_md = os.path.join(item_path, 'SKILL.md')
            
            if os.path.exists(skill_md):
                total_count += 1
                
                # 检查是否需要修复
                with open(skill_md, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if not content.startswith('---\n'):
                    if fix_yaml_frontmatter(item_path):
                        fixed_count += 1
    
    print(f"\n修复完成: {fixed_count}/{total_count} 个技能已修复")
    return fixed_count > 0

def main():
    """主函数"""
    print("快速技能修复工具")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        skills_dir = sys.argv[1]
    else:
        skills_dir = ""
    
    success = scan_and_fix_skills(skills_dir)
    
    if success:
        print("\n建议: 重启应用程序以确保技能重新加载")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
