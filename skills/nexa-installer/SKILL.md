---
name: nexa-installer
description: "上传Nexa CLI安装脚本并配置开机启动服务，支持远程部署和系统服务管理"
version: "1.0.0"
license: MIT License (见仓库根目录 LICENSE 文件)
---

## 我做什么

我是一个用于**远程安装和配置 Nexa AI 服务**的专业工具。我的核心功能包括：

1. **上传安装脚本**：将本地 Nexa CLI 安装脚本远程上传到目标主机
2. **执行安装**：在远程主机上执行安装脚本
3. **服务配置**：配置 Nexa 服务监听指定地址和端口（默认 0.0.0.0:18181）
4. **开机启动**：创建 systemd 服务并设置开机自启

## 何时使用我

当您需要以下场景时使用此技能：

- **首次部署**：在新的远程服务器上安装 Nexa AI 服务
- **批量部署**：使用 remote-manager 技能批量安装 Nexa 到多台服务器
- **服务迁移**：将 Nexa 服务迁移到新服务器
- **自动化部署**：在 CI/CD 流程中自动部署 Nexa 服务

## 使用流程

### 前置条件

1. **Nexa 安装脚本**：本地需要有一个 `.sh` 格式的 Nexa CLI 安装脚本
2. **远程主机配置**：使用 remote-manager 技能管理远程主机信息，或手动提供连接信息
3. **依赖安装**：
   ```bash
   pip install -r scripts/requirements.txt
   ```

### 目录结构

```
nexa-installer/
├── SKILL.md            # 技能主配置文件
├── config/             # 配置文件目录
│   └── config.example.json  # 配置文件示例
└── scripts/            # 脚本目录
    ├── main.py         # 主执行脚本（位于 scripts/main.py）
    └── requirements.txt # Python依赖文件（位于 scripts/requirements.txt）
```

> 注意：以上目录结构中使用斜杠(/)是为了文档显示清晰，实际文件路径会根据操作系统自动使用正确的分隔符（Windows使用反斜杠\，Unix/Linux/macOS使用斜杠/）

### 脚本索引

**编码声明**: 本技能所有脚本默认使用UTF-8编码，Windows系统下已配置UTF-8控制台输出。

| 脚本名称 | 脚本路径 | 功能描述 | 调用方式 |
|---------|---------|---------|---------|
| main.py | scripts/main.py | 主执行脚本：上传安装脚本并配置服务 | `python "路径/main.py" -h <主机名> -s <本地脚本路径>` |
| requirements.txt | scripts/requirements.txt | Python依赖列表 | `pip install -r "路径/requirements.txt"` |

### 使用方法

#### 方式一：使用 remote-manager 管理的主机

```bash
# 安装 Nexa CLI 并配置服务（默认配置）
python "scripts/main.py" -h <主机名> -s /path/to/nexa-cli.sh

# 指定自定义安装脚本和配置
python "scripts/main.py" -h <主机名> -s /path/to/nexa-cli.sh --host-addr 0.0.0.0 --port 18181

# 仅上传安装脚本，不执行安装
python "scripts/main.py" -h <主机名> -s /path/to/nexa-cli.sh --upload-only

# 仅执行安装，不上传脚本（脚本已存在）
python "scripts/main.py" -h <主机名> --install-only
```

#### 方式二：手动指定连接信息

```bash
python "scripts/main.py" --host <IP地址> -p <端口> -u <用户名> --password <密码> -s /path/to/nexa-cli.sh
```

### 参数说明

#### 必需参数

- `-s, --script-path`: 本地 Nexa CLI 安装脚本路径（.sh 文件）

#### 常用参数

- `-h, --host`: 目标主机名称（在 remote-manager 中配置的主机名）或 IP 地址
- `--host-addr`: 服务监听地址（默认: 0.0.0.0）
- `--port`: 服务监听端口（默认: 18181）
- `--upload-only`: 仅上传安装脚本，不执行安装
- `--install-only`: 仅执行安装，不上传脚本（脚本需已存在）
- `--no-service`: 不创建 systemd 服务

#### 远程连接参数（当不使用 remote-manager 时）

- `-p, --port`: SSH 端口（默认: 22）
- `-u, --username`: SSH 用户名（默认: root）
- `--password`: SSH 密码（或使用私钥认证）
- `-k, --private-key`: SSH 私钥文件路径

#### 其他参数

- `--skip-update`: 跳过版本检查
- `-v, --verbose`: 详细输出
- `--help`: 显示帮助信息

### 使用示例

#### 示例 1：基本使用

```bash
# 上传并安装 Nexa CLI，使用默认配置
python "scripts/main.py" -h nexa-server -s /sdcard/download/nexa-cli_linux_x86_64.sh
```

#### 示例 2：自定义端口和地址

```bash
# 监听 0.0.0.0:8080 端口
python "scripts/main.py" -h nexa-server -s /sdcard/download/nexa-cli.sh --host-addr 0.0.0.0 --port 8080
```

#### 示例 3：仅上传脚本

```bash
# 仅上传安装脚本，不执行安装
python "scripts/main.py" -h nexa-server -s /sdcard/download/nexa-cli.sh --upload-only
```

#### 示例 4：使用私钥认证

```bash
# 使用 SSH 私钥认证
python "scripts/main.py" -h nexa-server -s /sdcard/download/nexa-cli.sh -u root -k ~/.ssh/id_rsa
```

### 配置文件

#### 默认配置文件 (config/config.example.json)

```json
{
    "skill_name": "nexa-installer",
    "version": "1.0.0",
    "settings": {
        "output_dir": "output",
        "log_level": "info",
        "max_retries": 3
    },
    "installation": {
        "default_host": "0.0.0.0",
        "default_port": 18181,
        "service_name": "nexa",
        "service_description": "Nexa AI Service",
        "install_path": "/usr/local/bin",
        "remote_temp_dir": "/tmp"
    }
}
```

### 服务管理命令

安装完成后，可以使用以下命令管理 Nexa 服务：

```bash
# 查看服务状态
systemctl status nexa

# 启动服务
systemctl start nexa

# 停止服务
systemctl stop nexa

# 重启服务
systemctl restart nexa

# 禁用开机自启
systemctl disable nexa
```

### API 访问

安装完成后，可以通过以下地址访问 Nexa AI 服务：

- **API 文档**: http://<主机IP>:18181/docs
- **Web UI**: http://<主机IP>:18181/docs/ui

## 输出标准

### 输出文件规则（重要）

**规则**: 所有脚本生成的输出文件（如日志文件、临时文件等）必须保存到**当前工作目录**，而不是技能安装目录。

**原因**:
- 技能安装目录通常位于系统配置目录（如 `~/.config/opencode/skills/`）
- 用户希望在当前工作目录中看到输出结果
- 避免污染技能安装目录

**跨平台路径处理**: 在Python中处理路径时，始终使用 `os.path.join()` 来确保跨平台兼容性：

```python
import os

# 正确: 保存到当前工作目录（自动使用系统路径分隔符）
output_path = os.path.join(os.getcwd(), "output.txt")

# 正确: 构建多级路径（自动处理路径分隔符）
data_dir = os.path.join(os.getcwd(), "data", "output")
output_path = os.path.join(data_dir, "result.txt")
```

### 依赖管理

所有Python依赖必须记录在 scripts/requirements.txt 文件中：

```
pyyaml>=6.0
paramiko>=2.12.0
requests>=2.28.0
psutil>=5.9.0
```

## 常见问题

### Q: 安装脚本上传失败怎么办？

A: 检查以下事项：
1. 确认脚本文件存在且有执行权限
2. 检查网络连接
3. 使用 `--verbose` 参数查看详细错误信息
4. 确认远程主机磁盘空间充足

### Q: 服务启动失败怎么办？

A: 检查以下事项：
1. 查看服务日志：`journalctl -u nexa -n 50`
2. 确认端口未被占用：`ss -tlnp | grep 18181`
3. 确认 Nexa CLI 已正确安装：`which nexa`

### Q: 如何修改服务配置？

A: 修改 systemd 服务文件：
```bash
sudo nano /etc/systemd/system/nexa.service
# 修改 ExecStart 参数
sudo systemctl daemon-reload
sudo systemctl restart nexa
```

## 类别

运维工具、服务器管理、自动化部署、AI服务

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
- [ ] main.py示例脚本已创建（包含完整的安装功能）
- [ ] 所有脚本存放在scripts目录下

**输出规则验证**:
- [ ] 脚本使用 `os.getcwd()` 获取当前工作目录作为输出路径
- [ ] 输出文件不保存到技能安装目录