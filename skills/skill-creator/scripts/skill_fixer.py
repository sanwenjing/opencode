# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

#!/usr/bin/env python3
"""
技能修复工具 (Skill Fix Tool)

专门用于诊断和修复技能系统问题的工具集
作者: Claude Assistant
版本: 1.0
"""

import os
import re
import yaml
import json
import argparse
import shutil
from pathlib import Path
from typing import List, Dict, Tuple, Any
from datetime import datetime

class SkillFixer:
    """技能修复工具类"""
    
    def __init__(self, skills_dir: str = ""):
        self.skills_dir = skills_dir or os.path.join(os.path.dirname(__file__), "..", "..")
        self.issues = []
        self.fixes_applied = []
        
    def scan_skill_directories(self) -> List[str]:
        """扫描所有技能目录"""
        skill_dirs = []
        if os.path.exists(self.skills_dir):
            for item in os.listdir(self.skills_dir):
                item_path = os.path.join(self.skills_dir, item)
                if os.path.isdir(item_path) and not item.startswith('.') and item != 'node_modules':
                    skill_dirs.append(item_path)
        return skill_dirs
    
    def check_skill_directory(self, skill_dir: str) -> List[Dict[str, Any]]:
        """检查单个技能目录的问题"""
        issues = []
        skill_name = os.path.basename(skill_dir)
        
        # 检查 SKILL.md 文件是否存在
        skill_md_path = os.path.join(skill_dir, 'SKILL.md')
        if not os.path.exists(skill_md_path):
            issues.append({
                'type': 'missing_skill_md',
                'skill': skill_name,
                'severity': 'critical',
                'message': f'技能 {skill_name} 缺少 SKILL.md 文件',
                'fix_type': 'create_skill_md'
            })
            return issues
        
        # 检查 SKILL.md 文件内容
        try:
            with open(skill_md_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 检查 YAML front matter
            if not content.startswith('---\n'):
                issues.append({
                    'type': 'missing_yaml_frontmatter',
                    'skill': skill_name,
                    'severity': 'high',
                    'message': f'技能 {skill_name} 缺失 YAML front matter',
                    'fix_type': 'add_yaml_frontmatter',
                    'file_path': skill_md_path
                })
            else:
                # 解析 YAML front matter
                try:
                    yaml_end = content.find('\n---\n', 4)
                    yaml_content = content[4:yaml_end]
                    yaml_data = yaml.safe_load(yaml_content)
                    
                    # 检查必需字段
                    required_fields = ['name', 'description', 'license']
                    for field in required_fields:
                        if field not in yaml_data:
                            issues.append({
                                'type': 'missing_yaml_field',
                                'skill': skill_name,
                                'severity': 'medium',
                                'message': f'技能 {skill_name} YAML 缺少必需字段: {field}',
                                'fix_type': 'add_yaml_field',
                                'field': field,
                                'file_path': skill_md_path
                            })
                    
                    # 检查名称一致性
                    if yaml_data.get('name') != skill_name:
                        issues.append({
                            'type': 'name_mismatch',
                            'skill': skill_name,
                            'severity': 'medium',
                            'message': f'技能名称不一致: 目录名为 "{skill_name}"，YAML 中为 "{yaml_data.get("name")}"',
                            'fix_type': 'fix_name_mismatch',
                            'correct_name': skill_name,
                            'file_path': skill_md_path
                        })
                        
                except yaml.YAMLError as e:
                    issues.append({
                        'type': 'yaml_syntax_error',
                        'skill': skill_name,
                        'severity': 'high',
                        'message': f'技能 {skill_name} YAML 语法错误: {str(e)}',
                        'fix_type': 'fix_yaml_syntax',
                        'file_path': skill_md_path
                    })
                
        except UnicodeDecodeError:
            issues.append({
                'type': 'file_encoding_error',
                'skill': skill_name,
                'severity': 'high',
                'message': f'技能 {skill_name} SKILL.md 文件编码错误',
                'fix_type': 'fix_file_encoding',
                'file_path': skill_md_path
            })
        except Exception as e:
            issues.append({
                'type': 'file_read_error',
                'skill': skill_name,
                'severity': 'high',
                'message': f'无法读取技能 {skill_name} 的 SKILL.md: {str(e)}',
                'fix_type': 'fix_file_permissions',
                'file_path': skill_md_path
            })
        
        return issues
    
    def check_system_configuration(self) -> List[Dict[str, Any]]:
        """检查系统配置问题"""
        issues = []
        
        # 检查技能目录是否存在
        if not os.path.exists(self.skills_dir):
            issues.append({
                'type': 'missing_skills_directory',
                'severity': 'critical',
                'message': f'技能目录不存在: {self.skills_dir}',
                'fix_type': 'create_skills_directory'
            })
        
        return issues
    
    def check_cache_status(self) -> List[Dict[str, Any]]:
        """检查缓存状态"""
        issues = []
        cache_dirs = []
        
        # 查找所有 __pycache__ 目录
        for root, dirs, files in os.walk(self.skills_dir):
            if '__pycache__' in dirs:
                cache_dirs.append(os.path.join(root, '__pycache__'))
        
        if cache_dirs:
            issues.append({
                'type': 'cache_exists',
                'severity': 'low',
                'message': f'发现 {len(cache_dirs)} 个 Python 缓存目录',
                'fix_type': 'clear_cache',
                'cache_dirs': cache_dirs
            })
        
        return issues
    
    def fix_missing_yaml_frontmatter(self, issue: Dict[str, Any]) -> bool:
        """修复缺失的 YAML front matter"""
        file_path = issue['file_path']
        skill_name = issue['skill']
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # 从原始内容中提取信息
            lines = original_content.split('\n')
            title_line = lines[0] if lines else f"# {skill_name.replace('-', ' ').title()}"
            
            # 生成 YAML front matter
            yaml_frontmatter = f"""---
name: {skill_name}
description: "技能描述 - 需要手动完善具体功能和使用场景"
license: 专有。LICENSE.txt 包含完整条款
---

"""
            
            # 写入修复后的内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(yaml_frontmatter + original_content)
            
            self.fixes_applied.append(f'为技能 {skill_name} 添加了 YAML front matter')
            return True
            
        except Exception as e:
            print(f"修复 {skill_name} 的 YAML front matter 时出错: {str(e)}")
            return False
    
    def fix_missing_yaml_field(self, issue: Dict[str, Any]) -> bool:
        """修复缺失的 YAML 字段"""
        file_path = issue['file_path']
        field = issue['field']
        skill_name = issue['skill']
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 在 YAML front matter 中添加缺失字段
            yaml_end = content.find('\n---\n', 4)
            if yaml_end == -1:
                return False
            
            yaml_section = content[:yaml_end]
            
            if field == 'license':
                if 'license:' not in yaml_section:
                    new_yaml = yaml_section + f"\nlicense: 专有。LICENSE.txt 包含完整条款"
                    content = new_yaml + content[yaml_end:]
            elif field == 'name':
                if 'name:' not in yaml_section:
                    new_yaml = yaml_section + f"\nname: {skill_name}"
                    content = new_yaml + content[yaml_end:]
            elif field == 'description':
                if 'description:' not in yaml_section:
                    new_yaml = yaml_section + f'\ndescription: "{skill_name} 技能 - 需要完善功能描述"'
                    content = new_yaml + content[yaml_end:]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.fixes_applied.append(f'为技能 {skill_name} 添加了缺失字段: {field}')
            return True
            
        except Exception as e:
            print(f"修复 {skill_name} 的 YAML 字段 {field} 时出错: {str(e)}")
            return False
    
    def fix_name_mismatch(self, issue: Dict[str, Any]) -> bool:
        """修复名称不匹配问题"""
        file_path = issue['file_path']
        correct_name = issue['skill']
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换 YAML 中的 name 字段
            content = re.sub(
                r'^name:\s*.+$',
                f'name: {correct_name}',
                content,
                flags=re.MULTILINE
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.fixes_applied.append(f'修正了技能名称不匹配: 统一为 {correct_name}')
            return True
            
        except Exception as e:
            print(f"修复名称不匹配时出错: {str(e)}")
            return False
    
    def clear_cache(self, issue: Dict[str, Any]) -> bool:
        """清理缓存"""
        cache_dirs = issue.get('cache_dirs', [])
        cleared_count = 0
        
        for cache_dir in cache_dirs:
            try:
                shutil.rmtree(cache_dir)
                cleared_count += 1
            except Exception as e:
                print(f"清理缓存目录 {cache_dir} 时出错: {str(e)}")
        
        if cleared_count > 0:
            self.fixes_applied.append(f'清理了 {cleared_count} 个缓存目录')
            return True
        
        return False
    
    def apply_fixes(self, issues: List[Dict[str, Any]], auto_fix: bool = False) -> List[Dict[str, Any]]:
        """应用修复方案"""
        fixed_issues = []
        
        for issue in issues:
            if not auto_fix:
                print(f"\n发现问题: {issue['message']}")
                response = input("是否修复? (y/n): ").strip().lower()
                if response != 'y':
                    continue
            
            fix_applied = False
            
            if issue['fix_type'] == 'add_yaml_frontmatter':
                fix_applied = self.fix_missing_yaml_frontmatter(issue)
            elif issue['fix_type'] == 'add_yaml_field':
                fix_applied = self.fix_missing_yaml_field(issue)
            elif issue['fix_type'] == 'fix_name_mismatch':
                fix_applied = self.fix_name_mismatch(issue)
            elif issue['fix_type'] == 'clear_cache':
                fix_applied = self.clear_cache(issue)
            
            if fix_applied:
                fixed_issues.append(issue)
        
        return fixed_issues
    
    def diagnose(self) -> Dict[str, Any]:
        """执行完整诊断"""
        print("🔍 正在诊断技能系统...")
        
        all_issues = []
        
        # 检查技能目录
        skill_dirs = self.scan_skill_directories()
        print(f"发现 {len(skill_dirs)} 个技能目录")
        
        for skill_dir in skill_dirs:
            issues = self.check_skill_directory(skill_dir)
            all_issues.extend(issues)
        
        # 检查系统配置
        system_issues = self.check_system_configuration()
        all_issues.extend(system_issues)
        
        # 检查缓存
        cache_issues = self.check_cache_status()
        all_issues.extend(cache_issues)
        
        # 分类问题
        categorized = {
            'critical': [i for i in all_issues if i['severity'] == 'critical'],
            'high': [i for i in all_issues if i['severity'] == 'high'],
            'medium': [i for i in all_issues if i['severity'] == 'medium'],
            'low': [i for i in all_issues if i['severity'] == 'low']
        }
        
        return {
            'total_issues': len(all_issues),
            'issues_by_severity': categorized,
            'all_issues': all_issues,
            'skills_found': len(skill_dirs)
        }
    
    def generate_report(self, diagnosis: Dict[str, Any], output_file: str = "") -> str:
        """生成诊断报告"""
        report = []
        report.append("# 技能系统诊断报告")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        report.append(f"## 概要")
        report.append(f"- 发现技能: {diagnosis['skills_found']} 个")
        report.append(f"- 问题总数: {diagnosis['total_issues']} 个")
        report.append("")
        
        for severity, issues in diagnosis['issues_by_severity'].items():
            if issues:
                report.append(f"## {severity.upper()} 级别问题 ({len(issues)} 个)")
                for issue in issues:
                    report.append(f"- **{issue['skill']}**: {issue['message']}")
                report.append("")
        
        if self.fixes_applied:
            report.append("## 已应用的修复")
            for fix in self.fixes_applied:
                report.append(f"- {fix}")
            report.append("")
        
        report_text = '\n'.join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"📄 诊断报告已保存到: {output_file}")
        
        return report_text


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='技能修复工具')
    parser.add_argument('--skills-dir', default="", help='技能目录路径')
    parser.add_argument('--diagnose-only', action='store_true', help='仅诊断不修复')
    parser.add_argument('--auto-fix', action='store_true', help='自动修复所有问题')
    parser.add_argument('--interactive', action='store_true', help='交互式修复')
    parser.add_argument('--skill', help='指定要修复的技能')
    parser.add_argument('--output', default="", help='输出报告文件路径')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    fixer = SkillFixer(args.skills_dir or "")
    
    # 执行诊断
    diagnosis = fixer.diagnose()
    
    # 显示结果
    for severity, issues in diagnosis['issues_by_severity'].items():
        if issues and args.verbose:
            print(f"\n🚨 {severity.upper()} 级别问题 ({len(issues)} 个):")
            for issue in issues:
                print(f"  - {issue['message']}")
    
    # 生成报告
    report = fixer.generate_report(diagnosis, args.output or "")
    if not args.output and args.verbose:
        print("\n" + report)
    
    # 应用修复
    if not args.diagnose_only and diagnosis['total_issues'] > 0:
        if args.auto_fix or args.interactive:
            fixed_issues = fixer.apply_fixes(diagnosis['all_issues'], args.auto_fix)
            print(f"\n✅ 已修复 {len(fixed_issues)} 个问题")
        else:
            print(f"\n💡 使用 --auto-fix 或 --interactive 来修复问题")
    
    return diagnosis['total_issues']


if __name__ == '__main__':
    sys.exit(main() if main() > 0 else 0)
