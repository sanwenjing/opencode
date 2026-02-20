---
name: mqtt-client
description: "MQTT客户端工具，支持连接Broker、发布消息、订阅主题、接收消息等核心功能"
version: "1.0.0"
license: MIT License (见仓库根目录 LICENSE 文件)
---

## 我做什么

MQTT 客户端工具，提供完整的 MQTT 协议支持，包括：
- **连接管理**：连接到 MQTT Broker，支持用户名/密码认证和 TLS 加密
- **消息发布**：向指定主题发布消息，支持 QoS 0/1/2 和保留消息
- **主题订阅**：订阅一个或多个主题，实时接收消息
- **配置管理**：保存和管理 Broker 连接配置
- **消息持久化**：可选将接收的消息保存到文件

## 何时使用我

- 需要测试 MQTT Broker 连接
- 需要向物联网设备发送控制命令
- 需要接收传感器或设备上报的数据
- 需要调试 MQTT 通信
- 需要批量处理 MQTT 消息

## 使用流程

### 目录结构

```
mqtt-client/
├── SKILL.md              # 技能主配置文件
├── CHANGELOG.md          # 版本变更日志
├── config/               # 配置文件目录
│   └── mqtt_config.json  # MQTT 连接配置
├── scripts/              # 脚本目录
│   ├── main.py          # 主执行脚本
│   └── requirements.txt # Python 依赖文件
└── LICENSE.txt          # 许可证文件
```

### 配置文件目录（config/）

配置文件 `mqtt_config.json` 存放在 `config/` 目录下，用于保存 Broker 连接信息：

```json
{
  "host": "broker.emqx.io",
  "port": 1883,
  "username": "",
  "password": "",
  "use_tls": false,
  "client_id": "mqtt-client-xxx",
  "keepalive": 60
}
```

### 脚本索引

**编码声明**: 本技能所有脚本默认使用UTF-8编码，Windows系统下已配置UTF-8控制台输出。

| 脚本名称 | 脚本路径 | 功能描述 | 调用方式 |
|---------|---------|---------|---------|
| main.py | scripts/main.py | MQTT 客户端主程序 | `python scripts/main.py <命令> [选项]` |
| requirements.txt | scripts/requirements.txt | Python 依赖列表 | `pip install -r scripts/requirements.txt` |

### 使用方法

#### 1. 安装依赖

```bash
pip install -r /root/.config/opencode/skills/mqtt-client/scripts/requirements.txt
```

#### 2. 配置 Broker 连接

```bash
# 设置 Broker 地址和端口
python /root/.config/opencode/skills/mqtt-client/scripts/main.py config --set-host broker.emqx.io --set-port 1883

# 设置用户名和密码（如果需要）
python /root/.config/opencode/skills/mqtt-client/scripts/main.py config --set-username user --set-password pass

# 启用 TLS 加密
python /root/.config/opencode/skills/mqtt-client/scripts/main.py config --set-tls true

# 查看当前配置
python /root/.config/opencode/skills/mqtt-client/scripts/main.py config --show
```

#### 3. 发布消息

```bash
# 发布简单消息
python /root/.config/opencode/skills/mqtt-client/scripts/main.py pub -t test/topic -m "Hello MQTT"

# 发布 QoS 1 消息
python /root/.config/opencode/skills/mqtt-client/scripts/main.py pub -t test/topic -m "Important message" -q 1

# 发布保留消息
python /root/.config/opencode/skills/mqtt-client/scripts/main.py pub -t test/topic -m "Retained message" -r

# 指定 Broker 发布
python /root/.config/opencode/skills/mqtt-client/scripts/main.py pub -H broker.emqx.io -p 1883 -t test/topic -m "Hello"
```

#### 4. 订阅主题

```bash
# 订阅单个主题
python /root/.config/opencode/skills/mqtt-client/scripts/main.py sub -t test/topic

# 订阅并保存消息到文件
python /root/.config/opencode/skills/mqtt-client/scripts/main.py sub -t test/topic --save -o messages.txt

# 使用 QoS 1 订阅
python /root/.config/opencode/skills/mqtt-client/scripts/main.py sub -t test/topic -q 1

# 使用通配符订阅
python /root/.config/opencode/skills/mqtt-client/scripts/main.py sub -t "test/#"
```

#### 5. 连接并订阅多个主题

```bash
# 连接并订阅多个主题
python /root/.config/opencode/skills/mqtt-client/scripts/main.py connect -s test/topic1 -s test/topic2

# 连接、订阅并保存消息
python /root/.config/opencode/skills/mqtt-client/scripts/main.py connect -s test/# --save
```

### 命令参考

| 命令 | 说明 |
|-----|------|
| `config` | 配置管理，设置/查看 Broker 连接信息 |
| `pub` | 发布消息到指定主题 |
| `sub` | 订阅主题并接收消息 |
| `connect` | 连接到 Broker，可选订阅主题 |

### 常用选项

| 选项 | 说明 |
|-----|------|
| `-H, --host` | Broker 地址 |
| `-p, --port` | Broker 端口 |
| `-u, --username` | 用户名 |
| `-P, --password` | 密码 |
| `--tls` | 启用 TLS 加密 |
| `-t, --topic` | 主题 |
| `-m, --message` | 消息内容 |
| `-q, --qos` | QoS 等级 (0/1/2) |
| `-r, --retain` | 保留消息 |
| `-s, --save` | 保存消息到文件 |
| `-o, --output` | 输出文件名 |

## 输出标准

### 消息输出
- 订阅的消息实时打印到控制台
- 使用 `--save` 选项时，消息保存到当前工作目录的指定文件
- 消息格式：`[时间戳] 主题: 内容`

### 配置文件
- 配置文件保存在技能目录的 `config/mqtt_config.json`
- 使用 JSON 格式，UTF-8 编码

## 类别
网络通信、物联网、消息队列

## 验证清单

**基础验证**:
- [x] 技能名称通过正则表达式验证 `^[a-z0-9]+(-[a-z0-9]+)*$`
- [x] 名称长度在1-64字符范围内
- [x] 描述长度在1-1024字符范围内

**文件验证**:
- [x] YAML frontmatter格式正确
- [x] 所有必需字段存在（name, description, license）
- [x] SKILL.md文件编码为UTF-8

**目录结构验证**:
- [x] config目录已创建
- [x] scripts目录已创建
- [x] requirements.txt文件存在于scripts目录
- [x] main.py脚本已创建
- [x] 所有脚本存放在scripts目录下

**输出规则验证**:
- [x] 消息保存到当前工作目录
- [x] 配置文件保存到技能config目录
