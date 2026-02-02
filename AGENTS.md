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

## 技能创建规则
- 创建任何新技能时，默认使用 skill-creator 技能来创建
- 遵循 skill-creator 的标准流程和命名规范