---
name: remote-manager
description: 批量管理远程SSH主机的工具，支持维护主机信息表并批量执行命令获取结果
version: 1.0.2
license: 专有。LICENSE.txt 包含完整条款
---

## 我做什么

我是一个用于批量管理远程SSH主机的专业工具。我的主要功能包括：

1. **主机信息管理**：维护一个主机清单表，记录所有远程主机的地址、端口、用户名、密码（或私钥）、备注和用途等信息
2. **批量命令执行**：可以同时向所有主机或指定主机发送SSH命令，并获取执行结果
3. **数据导入导出**：支持从CSV文件导入主机列表，或导出为CSV/YAML格式进行备份
4. **灵活的主机控制**：支持启用/禁用特定主机，方便分组管理

## 何时使用我

当您需要以下场景时使用此技能：

- **批量更新**：同时在多台OpenCode服务器上执行更新操作（如 `git pull`）
- **状态检查**：批量检查所有服务器的运行状态（如 `systemctl status opencode`）
- **配置管理**：统一修改多台服务器的配置
- **日志收集**：批量获取多台服务器的日志文件
- **日常运维**：执行任何需要在多台服务器上同时进行的操作

## 使用流程

### 目录结构

```
remote-manager/
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
| main.py | scripts/main.py | 主执行脚本：主机管理、批量命令执行、导入导出 | `python "C:\Users\Administrator\.config\opencode\skills\remote-manager\scripts\main.py" [命令]` |
| requirements.txt | scripts/requirements.txt | Python依赖列表 | `pip install -r "C:\Users\Administrator\.config\opencode\skills\remote-manager\scripts\requirements.txt"` |

### 依赖安装

在使用技能之前，请先安装必要的依赖：

```bash
pip install -r "C:\Users\Administrator\.config\opencode\skills\remote-manager\scripts\requirements.txt"
```

### 主机管理命令

#### 添加主机

```bash
python "C:\Users\Administrator\.config\opencode\skills\remote-manager\scripts\main.py" add -n <名称> -h <地址> -p <端口> -u <用户名> -pwd <密码>
```

**参数说明**：
- `-n, --name`: 主机唯一名称标识（必需）
- `-h, --host`: 主机IP地址或域名（必需）
- `-p, --port`: SSH端口（默认: 22）
- `-u, --username`: 用户名（默认: root）
- `-pwd, --password`: 密码
- `-k, --private-key`: 私钥文件路径（可选，与密码二选一）
- `-P, --purpose`: 用途说明
- `-r, --remark`: 备注信息

**示例**：
```bash
# 添加使用密码认证的服务器
python "C:\Users\Administrator\.config\opencode\skills\remote-manager\scripts\main.py" add -n server-prod -h 192.168.1.100 -p 22 -u root -pwd yourpassword -P "生产环境" -r "主业务服务器"

# 添加使用私钥认证的服务器
python "C:\Users\Administrator\.config\opencode\skills\remote-manager\scripts\main.py" add -n server-dev -h dev.example.com -p 22 -u admin -k C:\keys\id_rsa -P "开发环境"
```

#### 列出所有主机

```bash
python "C:\Users\Administrator\.config\opencode\skills\remote-manager\scripts\main.py" list
```

**选项**：
- `-s, --show-passwords`: 显示密码（默认隐藏）

**示例**：
```bash
# 列出所有主机（隐藏密码）
python "C:\Users\Administrator\.config\opencode\skills\remote-manager\scripts\main.py" list

# 列出所有主机（显示密码）
python "C:\Users\Administrator\.config\opencode\skills\remote-manager\scripts\main.py" list -s
```

#### 更新主机信息

```bash
python "C:\Users\Administrator\.config\opencode\skills\remote-manager\scripts\main.py" update -n <名称> [选项]
```

**示例**：
```bash
# 修改端口和密码
python "C:\Users\Administrator\.config\opencode\skills\remote-manager\scripts\main.py" update -n server-prod -p 2222 -pwd newpassword

# 禁用某台主机
python "C:\Users\Administrator\.config\opencode\skills\remote-manager\scripts\main.py" update -n server-dev -e false
```

#### 删除主机

```bash
python "C:\Users\Administrator\.config\opencode\skills\remote-manager\scripts\main.py" remove -n <名称>
```

**示例**：
```bash
python "C:\Users\Administrator\.config\opencode\skills\remote-manager\scripts\main.py" remove -n server-old
```

### 批量执行命令

#### 执行命令

```bash
python "C:\Users\Administrator\.config\opencode\skills\remote-manager\scripts\main.py" exec -c "<命令>" [-n <主机名列表>] [-o <输出文件>]
```

**参数说明**：
- `-c, --command`: 要执行的命令（必需）
- `-n, --names`: 目标主机名称列表（留空则执行所有启用主机）
- `-o, --output`: 输出结果到JSON文件（可选）

**示例**：
```bash
# 在所有启用主机上执行
python "C:\Users\Administrator\.config\opencode\skills\remote-manager\scripts\main.py" exec -c "uptime"

# 在指定主机上执行
python "C:\Users\Administrator\.config\opencode\skills\remote-manager\scripts\main.py" exec -c "df -h" -n server-prod server-dev

# 更新OpenCode并保存结果
python "C:\Users\Administrator\.config\opencode\skills\remote-manager\scripts\main.py" exec -c "cd /opt/opencode && git pull" -n server-prod -o update_results.json

# 检查OpenCode服务状态
python "C:\Users\Administrator\.config\opencode\skills\remote-manager\scripts\main.py" exec -c "systemctl status opencode" -n all
```

### 导入导出功能

#### 从CSV导入

```bash
python "C:\Users\Administrator\.config\opencode\skills\remote-manager\scripts\main.py" import -f <文件路径>
```

**CSV格式要求**：
```csv
name,host,port,username,password,private_key_path,remark,purpose,enabled
server1,192.168.1.10,22,root,pass123,,,Web服务器,true
server2,192.168.1.11,22,admin,,/path/to/key,备份机器,true
```

#### 导出到CSV

```bash
python "C:\Users\Administrator\.config\opencode\skills\remote-manager\scripts\main.py" export -f <文件路径>
```

**示例**：
```bash
python "C:\Users\Administrator\.config\opencode\skills\remote-manager\scripts\main.py" export -f hosts_backup.csv
```

## 数据存储

### 主机配置文件

所有主机信息默认保存在当前目录下的 `hosts.yaml` 文件中：

```yaml
updated: '2024-01-15T10:30:00.000000'
hosts:
  - name: server-prod
    host: 192.168.1.100
    port: 22
    username: root
    password: yourpassword
    private_key_path: null
    remark: 主业务服务器
    purpose: 生产环境
    enabled: true
```

**重要提示**：
- 配置文件保存到**当前工作目录**，而非技能安装目录
- 配置文件包含敏感信息，请妥善保管
- 建议定期导出备份

## 输出文件规则（重要）

**规则**: 所有脚本生成的输出文件（如CSV备份、JSON结果等）必须保存到**当前工作目录**，而不是技能安装目录。

**原因**:
- 技能安装目录通常位于系统配置目录（如 `~/.config/opencode/skills/`）
- 用户希望在当前工作目录中看到输出结果
- 避免污染技能安装目录

**跨平台路径处理**:

在Python中处理文件路径时，始终使用 `os.path.join()` 来确保跨平台兼容性：

```python
import os

# 正确: 保存到当前工作目录（自动使用系统路径分隔符）
output_path = os.path.join(os.getcwd(), "output.txt")

# 正确: 构建多级路径（自动处理路径分隔符）
data_dir = os.path.join(os.getcwd(), "data", "output")
result_path = os.path.join(data_dir, "result.txt")
```

## 常见问题

### Q: 密码安全吗？

A: 密码以明文形式保存在 YAML 配置文件中。请确保：
- 使用强密码
- 配置文件权限设置为仅当前用户可读写
- 定期更换密码

### Q: 支持私钥认证吗？

A: 支持。在添加主机时使用 `-k` 参数指定私钥文件路径，替代密码认证。

### Q: 可以跳过某些主机吗？

A: 可以。使用 `update` 命令将主机的 `enabled` 设为 `false`，则批量执行时会跳过该主机。

### Q: 命令执行超时怎么办？

A: 默认超时时间为30秒。如需调整，可在代码中修改 `SSHExecutor` 类的 `timeout` 参数。

## 类别

运维工具、服务器管理、批量操作、SSH客户端

## 验证清单

**基础验证**：
- [ ] 技能名称通过正则表达式验证 `^[a-z0-9]+(-[a-z0-9]+)*$`
- [ ] 名称长度在1-64字符范围内
- [ ] 描述长度在1-1024字符范围内

**文件验证**：
- [ ] YAML frontmatter格式正确
- [ ] 所有必需字段存在（name, description, license）
- [ ] SKILL.md文件编码为UTF-8

**目录结构验证**：
- [ ] scripts目录已创建
- [ ] requirements.txt文件存在于scripts目录
- [ ] main.py主脚本已创建（包含完整的SSH和主机管理功能）
- [ ] 所有脚本存放在scripts目录下

**功能验证**：
- [ ] 支持主机添加功能
- [ ] 支持主机列表查看
- [ ] 支持主机更新和删除
- [ ] 支持批量命令执行
- [ ] 支持CSV导入导出
- [ ] 支持密码和私钥两种认证方式

**输出规则验证**：
- [ ] 脚本使用 `os.getcwd()` 获取当前工作目录作为输出路径
- [ ] 输出文件不保存到技能安装目录
