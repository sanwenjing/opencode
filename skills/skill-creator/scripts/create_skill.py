# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

#!/usr/bin/env python3
"""
技能创建工具 (Skill Creator Tool)

用于创建符合OpenCode规范的新技能
作者: Claude Assistant
版本: 1.0
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import Optional, List


class SkillCreator:
    """技能创建工具类"""
    
    # 必需字段的默认依赖
    DEFAULT_DEPENDENCIES = [
        "pyyaml>=6.0",
    ]
    
    def __init__(self, skills_dir: str = ""):
        self.skills_dir = skills_dir or os.path.join(os.path.dirname(__file__), "..", "..")
        self.errors = []
        
    def validate_skill_name(self, name: str) -> bool:
        """验证技能名称是否符合规范"""
        # 检查长度
        if not name or len(name) < 1 or len(name) > 64:
            self.errors.append("技能名称长度必须在1-64个字符之间")
            return False
        
        # 检查正则表达式: 只允许小写字母、数字和连字符
        pattern = r'^[a-z0-9]+(-[a-z0-9]+)*$'
        if not re.match(pattern, name):
            self.errors.append("技能名称只能包含小写字母、数字和连字符，不能以连字符开头或结尾，不能连续使用连字符")
            return False
        
        return True
    
    def validate_description(self, description: str) -> bool:
        """验证描述是否符合规范"""
        if not description or len(description) < 1:
            self.errors.append("技能描述不能为空")
            return False
        
        if len(description) > 1024:
            self.errors.append("技能描述不能超过1024个字符")
            return False
        
        return True
    
    def check_existing_skill(self, skill_name: str) -> bool:
        """检查技能是否已存在"""
        skill_path = os.path.join(self.skills_dir, skill_name)
        if os.path.exists(skill_path):
            self.errors.append(f"技能 {skill_name} 已存在")
            return False
        return True
    
    def generate_skill_md(self, skill_name: str, description: str) -> str:
        """生成SKILL.md文件内容"""
        content = f"""---
name: {skill_name}
description: "{description}"
license: 专有。LICENSE.txt 包含完整条款
---

## 我做什么

[在此处详细描述技能的核心功能和使用场景]

## 何时使用我

[描述在什么情况下应该使用此技能]

## 使用流程

### 目录结构

```
{skill_name}/
├── SKILL.md              # 技能主配置文件
├── scripts/              # 脚本目录
│   ├── main.py          # 主执行脚本（位于 scripts/main.py）
│   └── requirements.txt # Python依赖文件（位于 scripts/requirements.txt）
└── LICENSE.txt          # 许可证文件
```

### 脚本索引

**编码声明**: 本技能所有脚本默认使用UTF-8编码，Windows系统下已配置UTF-8控制台输出。

| 脚本名称 | 脚本路径 | 功能描述 | 调用方式 |
|---------|---------|---------|---------|
| main.py | scripts/main.py | 主执行脚本 | `python scripts/main.py` |
| requirements.txt | scripts/requirements.txt | Python依赖列表 | `pip install -r scripts/requirements.txt` |

### 使用方法

[详细的使用说明，包括示例代码]

## 输出标准

### 目录结构标准
创建的技能必须具有以下目录结构：

```
技能名/
├── SKILL.md          # 技能主配置文件
├── scripts/          # 脚本目录
│   ├── main.py      # 主脚本
│   └── requirements.txt  # Python依赖
└── LICENSE.txt      # 许可证文件
```

### 依赖管理
- 所有Python依赖必须记录在 scripts/requirements.txt 文件中
- 使用标准的pip requirements格式
- 建议指定最低版本号，如: `package>=1.0.0`
- 常用依赖包括: pyyaml, requests, beautifulsoup4 等

## 类别
开发工具

## 验证清单

**基础验证**:
- [ ] 技能名称通过正则表达式验证 `^[a-z0-9]+(-[a-z0-9]+)*$`
- [ ] 名称长度在1-64字符范围内
- [ ] 描述长度在1-1024字符范围内

**文件验证**:
- [ ] YAML frontmatter格式正确
- [ ] 所有必需字段存在（name, description, license）
- [ ] SKILL.md文件编码为UTF-8

**目录结构验证**:
- [ ] scripts目录已创建
- [ ] requirements.txt文件存在于scripts目录
- [ ] 所有脚本存放在scripts目录下
"""
        return content
    
    def generate_requirements_txt(self, dependencies: Optional[List[str]] = None) -> str:
        """生成requirements.txt文件内容"""
        deps = dependencies or self.DEFAULT_DEPENDENCIES
        content = "# Python依赖列表\n"
        content += "# 安装命令: pip install -r requirements.txt\n\n"
        
        for dep in deps:
            content += f"{dep}\n"
        
        content += "\n# 添加其他依赖请在此列出，格式: package>=version\n"
        content += "# 示例:\n"
        content += "# requests>=2.28.0\n"
        content += "# beautifulsoup4>=4.11.0\n"
        content += "# lxml>=4.9.0\n"
        
        return content
    
    def create_skill(self, skill_name: str, description: str, 
                     dependencies: Optional[List[str]] = None,
                     dry_run: bool = False) -> bool:
        """创建新技能"""
        print(f"正在创建技能: {skill_name}")
        
        # 验证输入
        if not self.validate_skill_name(skill_name):
            return False
        
        if not self.validate_description(description):
            return False
        
        if not self.check_existing_skill(skill_name):
            return False
        
        if self.errors:
            print("\n验证失败:")
            for error in self.errors:
                print(f"  - {error}")
            return False
        
        # 创建目录结构
        skill_path = os.path.join(self.skills_dir, skill_name)
        scripts_path = os.path.join(skill_path, "scripts")
        
        if dry_run:
            print(f"\n[模拟运行] 将创建以下结构:")
            print(f"  {skill_name}/")
            print(f"  ├── SKILL.md")
            print(f"  ├── scripts/")
            print(f"  │   └── requirements.txt")
            return True
        
        try:
            # 创建主目录
            os.makedirs(skill_path, exist_ok=False)
            print(f"创建目录: {skill_path}")
            
            # 创建scripts目录
            os.makedirs(scripts_path, exist_ok=False)
            print(f"创建目录: {scripts_path}")
            
            # 创建SKILL.md
            skill_md_content = self.generate_skill_md(skill_name, description)
            skill_md_path = os.path.join(skill_path, "SKILL.md")
            with open(skill_md_path, 'w', encoding='utf-8') as f:
                f.write(skill_md_content)
            print(f"创建文件: SKILL.md")
            
            # 创建requirements.txt
            req_content = self.generate_requirements_txt(dependencies)
            req_path = os.path.join(scripts_path, "requirements.txt")
            with open(req_path, 'w', encoding='utf-8') as f:
                f.write(req_content)
            print(f"创建文件: scripts/requirements.txt")
            
            print(f"\n技能 {skill_name} 创建成功!")
            print(f"位置: {skill_path}")
            print(f"\n后续步骤:")
            print(f"  1. 编辑 {skill_name}/SKILL.md 完善技能描述")
            print(f"  2. 在 scripts/ 目录下添加脚本文件")
            print(f"  3. 根据需要修改 scripts/requirements.txt 添加依赖")
            print(f"  4. 安装依赖: pip install -r {skill_name}/scripts/requirements.txt")
            
            return True
            
        except Exception as e:
            print(f"创建技能时出错: {str(e)}")
            return False
    
    def update_requirements(self, skill_name: str, dependencies: List[str]) -> bool:
        """更新现有技能的requirements.txt"""
        skill_path = os.path.join(self.skills_dir, skill_name)
        scripts_path = os.path.join(skill_path, "scripts")
        req_path = os.path.join(scripts_path, "requirements.txt")
        
        if not os.path.exists(skill_path):
            print(f"错误: 技能 {skill_name} 不存在")
            return False
        
        try:
            # 确保scripts目录存在
            if not os.path.exists(scripts_path):
                os.makedirs(scripts_path)
                print(f"创建目录: scripts/")
            
            # 读取现有依赖（如果文件存在）
            existing_deps = []
            if os.path.exists(req_path):
                with open(req_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            existing_deps.append(line)
                print(f"找到现有依赖: {len(existing_deps)} 个")
            
            # 合并依赖（去重）
            all_deps = list(set(existing_deps + dependencies))
            all_deps.sort()  # 排序以便阅读
            
            # 生成新的requirements.txt
            req_content = self.generate_requirements_txt(all_deps)
            with open(req_path, 'w', encoding='utf-8') as f:
                f.write(req_content)
            
            action = "更新" if existing_deps else "创建"
            print(f"{action}文件: scripts/requirements.txt")
            print(f"总依赖数: {len(all_deps)} 个")
            
            return True
            
        except Exception as e:
            print(f"更新requirements.txt时出错: {str(e)}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='技能创建工具 - 创建符合OpenCode规范的新技能',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 创建新技能
  python scripts/create_skill.py my-new-skill "这是一个新技能的描述"
  
  # 创建技能并指定依赖
  python scripts/create_skill.py my-new-skill "技能描述" --deps pyyaml requests
  
  # 模拟运行（不实际创建）
  python scripts/create_skill.py my-new-skill "描述" --dry-run
  
  # 更新现有技能的依赖
  python scripts/create_skill.py --update-deps my-existing-skill --deps numpy pandas
        """
    )
    
    parser.add_argument('name', nargs='?', help='技能名称（仅包含小写字母、数字和连字符）')
    parser.add_argument('description', nargs='?', help='技能描述（1-1024字符）')
    parser.add_argument('--skills-dir', default="", help='技能目录路径（默认: ../../）')
    parser.add_argument('--deps', nargs='+', help='Python依赖包列表（如: pyyaml requests）')
    parser.add_argument('--dry-run', action='store_true', help='模拟运行，不实际创建文件')
    parser.add_argument('--update-deps', action='store_true', help='更新现有技能的依赖')
    
    args = parser.parse_args()
    
    creator = SkillCreator(args.skills_dir)
    
    if args.update_deps:
        # 更新依赖模式
        if not args.name:
            print("错误: 更新依赖时必须指定技能名称")
            return 1
        
        deps = args.deps or []
        if not deps:
            print("警告: 未指定依赖，将只确保requirements.txt存在")
        
        success = creator.update_requirements(args.name, deps)
        return 0 if success else 1
    
    # 创建新模式
    if not args.name or not args.description:
        parser.print_help()
        return 1
    
    success = creator.create_skill(
        skill_name=args.name,
        description=args.description,
        dependencies=args.deps,
        dry_run=args.dry_run
    )
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
