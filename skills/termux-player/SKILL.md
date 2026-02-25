---
name: termux-player
description: "远程Termux设备播放音乐工具，支持播放、暂停、停止、查看播放信息"
version: "1.0.0"
depends:
  - skill: remote-manager
  - skill: termux-api-controller
license: MIT License (见仓库根目录 LICENSE 文件)
---

## 我做什么

在远程Termux设备上播放音乐，支持播放指定音乐文件、暂停、继续、停止播放、查看播放信息等功能。

## 何时使用我

当需要远程控制Termux设备播放音乐时使用此技能。

## 目录结构

```
termux-music-player/
├── SKILL.md              # 技能主配置文件
├── config/               # 配置文件目录
└── scripts/              # 脚本目录
    ├── main.py          # 主执行脚本
    └── requirements.txt # Python依赖文件
```

## 脚本索引

**编码声明**: 本技能所有脚本默认使用UTF-8编码，Windows系统下已配置UTF-8控制台输出。

| 脚本名称 | 脚本路径 | 功能描述 | 调用方式 |
|---------|---------|---------|---------|
| main.py | scripts/main.py | Termux音乐播放器 | `python3 "/root/.config/opencode/skills/termux-music-player/scripts/main.py" [命令] [参数]` |

## 使用方法

### 列出音乐文件

```bash
python3 "/root/.config/opencode/skills/termux-music-player/scripts/main.py" list --host termux74
```

### 播放音乐

```bash
python3 "/root/.config/opencode/skills/termux-music-player/scripts/main.py" play "/sdcard/Download/music/歌曲名.mp3" --host termux74
```

### 暂停播放

```bash
python3 "/root/.config/opencode/skills/termux-music-player/scripts/main.py" pause --host termux74
```

### 继续播放

```bash
python3 "/root/.config/opencode/skills/termux-music-player/scripts/main.py" resume --host termux74
```

### 停止播放

```bash
python3 "/root/.config/opencode/skills/termux-music-player/scripts/main.py" stop --host termux74
```

### 查看播放信息

```bash
python3 "/root/.config/opencode/skillsusic-player/scripts/main/termux-m.py" info --host termux74
```

## 输出文件规则

所有脚本生成的输出文件必须保存到**当前工作目录**。

## 类别

移动设备控制、音乐播放

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
- [x] main.py主脚本已创建

**输出规则验证**:
- [x] 脚本使用 `os.getcwd()` 获取当前工作目录作为输出路径
