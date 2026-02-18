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
        self.path_sep = os.sep  # 系统路径分隔符（Windows: \, Unix/Linux/macOS: /）

    def format_path_for_display(self, *parts: str) -> str:
        """格式化路径用于显示（使用当前系统的路径分隔符）"""
        return self.path_sep.join(parts)
        
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
        sep = self.path_sep
        path_sep_display = '/' if sep == '/' else '\\\\'
        
        # 目录结构使用斜杠显示（更通用），但实际路径使用系统分隔符
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
├── config/               # 配置文件目录（保存技能脚本使用的所有配置文件）
├── scripts/              # 脚本目录
│   ├── main.py          # 主执行脚本（位于 scripts/main.py）
│   └── requirements.txt # Python依赖文件（位于 scripts/requirements.txt）
└── LICENSE.txt          # 许可证文件
```

> 注意：以上目录结构中使用斜杠(/)是为了文档显示清晰，实际文件路径会根据操作系统自动使用正确的分隔符（Windows使用反斜杠\\，Unix/Linux/macOS使用斜杠/）

### 配置文件目录（config/）

所有技能脚本使用的配置文件都应放在 `config/` 目录下，例如：
- API 配置文件（如 config/api_config.json）
- 模板文件（如 config/templates/）
- 数据文件（如 config/data/）

脚本中加载配置文件时应使用绝对路径或相对于当前工作目录的路径。

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
├── config/           # 配置文件目录（保存技能脚本使用的所有配置文件）
├── scripts/          # 脚本目录
│   ├── main.py      # 主脚本
│   └── requirements.txt  # Python依赖
└── LICENSE.txt      # 许可证文件
```

### 配置文件目录规则（重要）
**config/ 目录用途**：专门用于存放技能脚本运行时所需的所有配置文件。

**配置文件类型**：
- API 配置文件（如 api_config.json, credentials.ini）
- 模板文件（如 templates/*.j2）
- 数据文件（如 data/*.json, data/*.csv）
- 环境变量文件（如 .env 示例文件）
- 其他运行时配置文件

**配置文件加载方式**：
```python
import os

# 方式一：相对于当前工作目录加载配置文件（推荐）
config_path = os.path.join(os.getcwd(), "config", "settings.json")

# 方式二：相对于技能目录加载（不推荐，可能导致路径问题）
# skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# config_path = os.path.join(skill_dir, "config", "settings.json")
```

**重要**：配置文件应放在 config/ 目录下，而不是硬编码在脚本中或放在 scripts/ 目录下。

### 输出文件规则（重要）
**规则**: 所有脚本生成的输出文件（如下载的文件、生成的报告、输出的数据等）必须保存到**当前工作目录**，而不是技能安装目录。

**原因**:
- 技能安装目录通常位于系统配置目录（如 `~/.config/opencode/skills/`）
- 用户希望在当前工作目录中看到输出结果
- 避免污染技能安装目录

**跨平台路径处理**:
在Python中处理路径时，始终使用 `os.path.join()` 来确保跨平台兼容性：
- Windows系统会自动使用反斜杠 `\\` 作为路径分隔符
- Unix/Linux/macOS系统会自动使用斜杠 `/` 作为路径分隔符
- `os.path.join()` 会根据操作系统自动选择正确的分隔符

**实现方法**:
```python
import os

# 正确: 保存到当前工作目录（自动使用系统路径分隔符）
output_path = os.path.join(os.getcwd(), "output.txt")

# 正确: 构建多级路径（自动处理路径分隔符）
data_dir = os.path.join(os.getcwd(), "data", "output")
output_path = os.path.join(data_dir, "result.txt")

# 错误: 不要保存到脚本所在目录
# script_dir = os.path.dirname(os.path.abspath(__file__))
# output_path = os.path.join(script_dir, "output.txt")

# 错误: 不要硬编码路径分隔符
# output_path = "C:\\Users\\user\\data\\output.txt"  # 仅限Windows
# output_path = "/home/user/data/output.txt"  # 仅限Unix/Linux/macOS
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
- [ ] config目录已创建（用于存放配置文件）
- [ ] scripts目录已创建
- [ ] requirements.txt文件存在于scripts目录
- [ ] main.py示例脚本已创建（包含输出到当前工作目录的示例）
- [ ] 所有脚本存放在scripts目录下

**输出规则验证**:
- [ ] 脚本使用 `os.getcwd()` 获取当前工作目录作为输出路径
- [ ] 输出文件不保存到技能安装目录
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
    
    def generate_main_script(self, skill_name: str) -> str:
        """生成示例主脚本文件内容"""
        path_sep = self.path_sep
        
        # 转义大括号以避免在 f-string 中被解析
        template = '''# 设置控制台编码为UTF-8
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os

# 获取当前系统路径分隔符
PATH_SEP = os.sep


def get_output_path(filename: str) -> str:
    """
    获取输出文件的完整路径
    规则: 所有输出文件保存到当前工作目录，而不是技能安装目录

    例如:
    - 当前目录: C:\\Users\\用户\\projects (Windows) 或 /home/user/projects (Unix/Linux/macOS)
    - 技能安装目录: C:\\Users\\用户\\.config\\opencode\\skills\\''' + skill_name + '''\\ (Windows) 或 ~/.config/opencode/skills/''' + skill_name + '''/ (Unix/Linux/macOS)
    - 返回: 当前工作目录与filename拼接的路径
    """
    # 使用当前工作目录，而不是脚本所在目录
    return os.path.join(os.getcwd(), filename)


def main():
    """主函数示例"""
    # 示例: 创建一个输出文件到当前工作目录
    output_file = get_output_path("output.txt")
    
    print(f"工作目录: {os.getcwd()}")
    print(f"输出文件: {output_file}")
    
    # 写入示例内容
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("这是一个示例输出文件\\n")
    
    print(f"文件已保存到: {output_file}")


if __name__ == '__main__':
    main()
'''
        return template
    
    def generate_config_example(self) -> str:
        """生成示例配置文件内容"""
        content = """{
    "skill_name": "your-skill-name",
    "version": "1.0.0",
    "settings": {
        "output_dir": "output",
        "log_level": "info",
        "max_retries": 3
    },
    "api": {
        "enabled": false,
        "api_key": "",
        "base_url": ""
    },
    "data": {
        "cache_enabled": true,
        "cache_ttl": 3600
    }
}
"""
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
        config_path = os.path.join(skill_path, "config")
        
        if dry_run:
            print(f"\n[模拟运行] 将创建以下结构:")
            print(f"  {skill_name}{self.path_sep}")
            print(f"  ├── SKILL.md")
            print(f"  ├── config{self.path_sep}             # 配置文件目录")
            print(f"  ├── scripts{self.path_sep}")
            print(f"  │   ├── main.py           # 示例脚本（包含输出到当前工作目录的规则和跨平台路径处理）")
            print(f"  │   └── requirements.txt")
            print(f"\n注意: 实际路径分隔符会根据操作系统自动调整")
            print(f"  Windows: 使用反斜杠 (\\)")
            print(f"  Unix/Linux/macOS: 使用斜杠 (/)")
            return True
        
        try:
            # 创建主目录
            os.makedirs(skill_path, exist_ok=False)
            print(f"创建目录: {skill_path}")
            
            # 创建scripts目录
            os.makedirs(scripts_path, exist_ok=False)
            print(f"创建目录: {scripts_path}")
            
            # 创建config目录
            os.makedirs(config_path, exist_ok=False)
            print(f"创建目录: {config_path}")
            
            # 创建示例配置文件
            config_example = self.generate_config_example()
            config_example_path = os.path.join(config_path, "config.example.json")
            with open(config_example_path, 'w', encoding='utf-8') as f:
                f.write(config_example)
            print(f"创建文件: config/config.example.json")
            
            # 创建SKILL.md
            skill_md_content = self.generate_skill_md(skill_name, description)
            skill_md_path = os.path.join(skill_path, "SKILL.md")
            with open(skill_md_path, 'w', encoding='utf-8') as f:
                f.write(skill_md_content)
            print(f"创建文件: SKILL.md")
            
            # 创建示例主脚本
            main_script_content = self.generate_main_script(skill_name)
            main_script_path = os.path.join(scripts_path, "main.py")
            with open(main_script_path, 'w', encoding='utf-8') as f:
                f.write(main_script_content)
            print(f"创建文件: scripts/main.py")
            
            # 创建requirements.txt
            req_content = self.generate_requirements_txt(dependencies)
            req_path = os.path.join(scripts_path, "requirements.txt")
            with open(req_path, 'w', encoding='utf-8') as f:
                f.write(req_content)
            print(f"创建文件: scripts/requirements.txt")
            
            print(f"\n技能 {skill_name} 创建成功!")
            print(f"位置: {skill_path}")
            print(f"\n后续步骤:")
            print(f"  1. 编辑 {self.format_path_for_display(skill_name, 'SKILL.md')} 完善技能描述")
            print(f"  2. 编辑 {self.format_path_for_display('config', 'config.example.json')} 添加你的配置项")
            print(f"  3. 编辑 {self.format_path_for_display('scripts', 'main.py')} 添加你的功能代码")
            print(f"  4. 根据需要修改 {self.format_path_for_display('scripts', 'requirements.txt')} 添加依赖")
            print(f"  5. 安装依赖: pip install -r {self.format_path_for_display(skill_name, 'scripts', 'requirements.txt')}")
            
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
