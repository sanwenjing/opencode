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

## 技能创建规则
- 创建任何新技能时，默认使用 skill-creator 技能来创建
- 遵循 skill-creator 的标准流程和命名规范