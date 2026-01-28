#!/usr/bin/env python3
"""
安全技能修复工具 (Safe Skill Fix Tool)

安全地修复技能问题的工具，避免重复修复
"""

import os
import re
import sys
from pathlib import Path

def has_valid_yaml_frontmatter(content: str) -> bool:
    """检查是否有有效的 YAML front matter"""
    if not content.startswith('---\\n'):
        return False
    
    # 查找第二个 ---
    second_dash = content.find('\\n---\\n', 4)
    if second_dash == -1:
        return False
    
    return True

def extract_first_line_title(content: str) -> str:
    """提取第一行的标题"""
    lines = content.split('\\n')
    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            return line.replace('#', '').strip()
    
    return "技能工具"

def clean_skill_file(file_path: str) -> bool:
    """清理技能文件，移除重复的 YAML front matter"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找所有 YAML front matter 块
        yaml_blocks = []
        start = 0
        while True:
            if content.startswith('---\\n', start):
                second_dash = content.find('\\n---\\n', start + 4)
                if second_dash != -1:
                    yaml_blocks.append((start, second_dash + 5))
                    start = second_dash + 5
                else:
                    break
            else:
                break
        
        if len(yaml_blocks) <= 1:
            return True  # 不需要清理
        
        # 只保留第一个 YAML front matter
        first_block = yaml_blocks[0]
        yaml_content = content[first_block[0]:first_block[1]]
        remaining_content = content[first_block[1]:]
        
        # 移除后续的 YAML front matter
        for block in yaml_blocks[1:]:
            remaining_content = remaining_content.replace(content[block[0]:block[1]], '')
        
        # 清理多余的空行
        remaining_content = re.sub(r'\\n{3,}', '\\n\\n', remaining_content)
        remaining_content = remaining_content.lstrip('\\n')
        
        # 写入清理后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content + remaining_content)
        
        print(f"清理了文件: {file_path}")
        return True
        
    except Exception as e:
        print(f"清理文件 {file_path} 时出错: {str(e)}")
        return False

def add_yaml_frontmatter_safely(skill_dir: str) -> bool:
    """安全地为技能添加 YAML front matter"""
    skill_name = os.path.basename(skill_dir)
    skill_md = os.path.join(skill_dir, 'SKILL.md')
    
    if not os.path.exists(skill_md):
        return False
    
    try:
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 如果已经有有效的 YAML front matter，跳过
        if has_valid_yaml_frontmatter(content):
            return True
        
        # 清理重复的 YAML front matter
        if '---' in content:
            if not clean_skill_file(skill_md):
                return False
            
            # 重新读取清理后的内容
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()
        
        # 获取技能名称
        skill_name = os.path.basename(skill_dir)
        
        # 提取标题
        title = extract_first_line_title(content)
        
        # 生成 YAML front matter
        yaml_block = f"""---
name: {skill_name}
description: "{title} - 专业的技能工具"
license: 专有。LICENSE.txt 包含完整条款
---

"""
        
        # 写入文件
        with open(skill_md, 'w', encoding='utf-8') as f:
            f.write(yaml_block + content)
        
        print(f"修复了技能 {skill_name}")
        return True
        
    except Exception as e:
        print(f"修复 {skill_name} 时出错: {str(e)}")
        return False

def scan_and_fix_all_skills(skills_dir: str = ""):
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
                
                if add_yaml_frontmatter_safely(item_path):
                    fixed_count += 1
    
    print(f"\\n修复完成: {fixed_count}/{total_count} 个技能已处理")
    return fixed_count

def main():
    """主函数"""
    print("安全技能修复工具")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        skills_dir = sys.argv[1]
    else:
        skills_dir = ""
    
    success = scan_and_fix_all_skills(skills_dir)
    
    if success > 0:
        print("\\n建议: 重启应用程序以确保技能重新加载")
    
    return 0 if success > 0 else 1

if __name__ == '__main__':
    sys.exit(main())