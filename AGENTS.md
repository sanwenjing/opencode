# 全局规则配置
所有回答必须使用中文。

## 语言规则
- 回答必须使用简体中文
- 代码注释可以使用英文，但解释和说明必须用中文
- 错误信息和提示必须用中文
- 所有用户交互必须使用中文

## 交流风格
- 使用专业但友好的中文交流风格
- 技术术语可以保留英文原词并提供中文解释
- 回答应简洁明了，直接回应用户问题

## 代码相关
- 代码示例保持原样，但解释使用中文
- 变量名和函数名可以保持英文
- 提交信息使用中文
- 代码中禁止使用emoji
- Python脚本开头必须添加UTF-8编码设置：
  ```python
  # 设置控制台编码为UTF-8
  import sys
  if sys.platform == 'win32':
      import io
      sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
      sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
  ```

## 路径处理规则（重要）
- **跨平台路径处理**：创建脚本时必须判断当前系统环境，确保使用正确的路径分隔符
- **禁止硬编码路径分隔符**：
  - 禁止在代码中直接使用 `/` 或 `\\` 作为路径分隔符
  - 必须使用 `os.path.join()` 来构建路径，它会根据操作系统自动选择正确的分隔符
    - Windows: 自动使用反斜杠 `\`
    - Unix/Linux/macOS: 自动使用斜杠 `/`
- **路径显示规范**：
  - 在用户可见的输出中（如日志、提示信息、文档），使用当前系统的路径分隔符
  - 可以使用 `os.sep` 获取系统路径分隔符，`os.path.normpath()` 规范化路径
- **正确示例**：
  ```python
  import os
  
  # 正确：使用 os.path.join() 构建路径
  output_path = os.path.join(os.getcwd(), "output.txt")
  data_dir = os.path.join(os.getcwd(), "data", "output")
  result_path = os.path.join(data_dir, "result.txt")
  
  # 获取系统路径分隔符（如需显示）
  path_sep = os.sep  # Windows: \\, Unix/Linux/macOS: /
  ```
- **错误示例**：
  ```python
  # 错误：硬编码路径分隔符
  output_path = "C:\\Users\\user\\data\\output.txt"  # 仅限Windows
  output_path = "/home/user/data/output.txt"  # 仅限Unix/Linux/macOS
  
  # 错误：混用分隔符
  output_path = "data/output.txt"  # Windows上会失败
  ```

## 配置文件管理规则（重要）
- **配置文件存放位置**：所有技能的配置文件必须存放在技能目录下的 `config/` 文件夹中
- **配置文件读写规则**：
  - 读取配置文件时，优先从技能目录的 `config/` 文件夹中读取
  - 修改或生成配置文件时，默认保存到技能目录的 `config/` 文件夹中
  - 配置文件命名规范：`config.json` 或 `*.config.json`
- **配置文件加载方式**：
  ```python
  import os
  
  # 正确：从技能目录的config文件夹读取配置文件
  skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  config_path = os.path.join(skill_dir, "config", "config.json")
  
  # 错误：不要从当前工作目录读取配置文件
  # config_path = os.path.join(os.getcwd(), "config.json")
  ```
- **示例配置文件**：技能目录下的 `config/config.example.json` 作为配置文件的模板示例

## 脚本执行规则（重要）
- 使用skill的脚本时，禁止使用 `cd` 命令切换到脚本目录执行
- 必须使用脚本的绝对路径直接执行
- **Python脚本执行规则**：
  - 所有Python脚本必须使用 `python3` 命令执行
  - 如果系统没有 `python3` 命令但有 `python` 命令，需要创建软链接：
    ```bash
    # 检查python3是否存在
    which python3 || which python
    # 如果没有python3但有python，创建软链接
    sudo ln -s "$(which python)" /usr/bin/python3
    ```
  - 在调用任何Python脚本前，先检查python3是否可用，不可用时创建软链接
- 正确方式：`python3 "C:\Users\xxx\skills\skill-name\scripts\script.py"`
- 错误方式：`cd "C:\Users\xxx\skills\skill-name" && python scripts/script.py`
- 原因：避免路径污染和执行位置不确定性问题

## 任务执行规则（重要）
- 执行任何任务时，优先从可用技能列表中寻找合适的技能来处理
- 只有当没有匹配的技能时才自行处理任务
- 通过 `skill` 工具加载并使用对应的技能来处理特定领域的任务

## 技能管理规则（重要）

所有技能相关的操作（创建、修改、版本更新）**必须**通过 skill-creator 技能来处理：

### 技能创建
- 创建新技能时，使用 skill-creator 技能
- 遵循 skill-creator 的标准流程和命名规范
- 自动创建标准目录结构和初始文件

### 技能修改与版本管理
- **禁止**直接修改技能的版本号和CHANGELOG
- 修改技能后，使用 skill-creator 的 version_manager.py 脚本更新版本
- 所有版本号递增和CHANGELOG记录由 skill-creator 统一管理

### 使用方式
```bash
# 创建新技能
python3 "C:\Users\Administrator\.config\opencode\skills\skill-creator\scripts\create_skill.py" <技能名> <描述>

# 更新技能版本（自动更新版本号和CHANGELOG）
python3 "C:\Users\Administrator\.config\opencode\skills\skill-creator\scripts\version_manager.py" --skill <技能名> --bump <patch|minor|major> --message "变更描述"

# 查看技能版本信息
python3 "C:\Users\Administrator\.config\opencode\skills\skill-creator\scripts\version_manager.py" --skill <技能名> --info
```

### 技能修改规范（重要）
- **禁止直接修改技能文件**：所有技能修改必须通过 skill-creator 流程
- **修改前**：先读取 SKILL.md 了解当前版本和依赖
- **修改时**：
  1. 修改代码
  2. 在 SKILL.md 的 YAML front matter 中添加 `depends` 声明依赖的技能
  3. 使用 version_manager.py 更新版本号和 CHANGELOG
- **依赖声明格式**：
  ```yaml
  depends:
    - skill: remote-manager
    - skill: termux-api-controller
  ```

## Git 操作规则（重要）

### Git Push 规则
- **禁止手动执行 git push**：所有 git push 操作必须通过 git-push-notify 技能执行
- **必须使用技能**：`python3 "C:\Users\Administrator\.config\opencode\skills\git-push-notify\scripts\main.py" --repo <仓库路径>`
- **失败重试机制**：
  - 遇到网络失败时自动重试
  - 最大重试次数：10 次
  - 超过 10 次重试直接退出并报错
- **失败处理**：失败时仅记录日志，不发送通知
- **邮件通知**：成功时自动发送邮件和手机通知

### Git Push 条件（重要）
- **不自动 push**：每次提交后不自动执行 git push
- **触发条件**（满足任一条件才执行 git push）：
  1. 距离上次 push 超过 24 小时
  2. 本地领先远程 5 个或更多提交
- **检查方式**：使用 `git log --oneline origin/main..HEAD | wc -l` 检查领先提交数

### Git 提交安全检查（重要）
- **提交前检查**：每次 git commit 前必须检查技能 config 目录下的配置文件是否包含敏感信息
- **检查范围**：仅检查 `skills/*/config/` 目录下的文件
- **密码检查**：检查以下关键字（不区分大小写）：
  - password、passwd、pwd
  - secret、token、api_key、apikey
  - auth、credential
  - smtp_password、smtp_password
- **处理流程**：
  1. 如果配置文件包含密码或密钥，必须取消 git 追踪：`git rm --cached <文件路径>`
  2. 将文件路径加入到 `.gitignore`
  3. 重新添加其他文件并提交
- **配置文件规范**：所有含密码的配置必须存放在 `config/` 目录，并已在 `.gitignore` 中排除