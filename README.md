# OpenCode 配置仓库

OpenCode AI 编程助手的配置文件和技能集合。

## 目录结构

```
opencode/
├── AGENTS.md          # 全局规则配置
├── opencode.json      # OpenCode 主配置
├── .gitignore         # Git 忽略规则
└── skills/            # 技能目录
    ├── email-sender/           # 邮件发送工具
    ├── git-push-notify/        # Git Push 通知工具
    ├── remote-manager/         # 远程主机管理
    ├── termux-api-controller/  # Termux API 控制器
    ├── skill-creator/          # 技能创建工具
    ├── pdf/                    # PDF 处理工具
    ├── xlsx/                   # Excel 处理工具
    ├── docx/                   # Word 处理工具
    ├── pptx/                   # PPT 处理工具
    └── ...                     # 更多技能
```

## 主要技能说明

### 开发工具
- **skill-creator**: 技能创建和管理工具，遵循 OpenCode 规范
- **git-push-notify**: Git Push 自动化工具，支持邮件和手机通知
- **remote-manager**: 远程 SSH 主机批量管理工具
- **mcp-builder**: MCP 服务构建工具

### 文档处理
- **pdf**: PDF 文档处理
- **xlsx**: Excel 表格处理
- **docx**: Word 文档处理
- **pptx**: PowerPoint 演示文稿处理

### 移动设备
- **termux-api-controller**: Termux API 远程控制工具

### 通信工具
- **email-sender**: 专业邮件发送工具，支持附件和日志
- **internal-comms**: 内部通信工具

### 其他工具
- **duplicate_file_cleaner**: 重复文件清理
- **audio-encoding-fixer**: 音频编码修复
- **filename-to-music-tags**: 文件名转音乐标签
- **bilibili-downloader**: B站视频下载
- **news-fetcher**: 新闻获取
- **mirror-downloader**: 镜像下载

## 全局规则

详见 [AGENTS.md](./AGENTS.md)，包含：

- 语言规则（中文优先）
- 代码规范
- 路径处理规则
- 配置文件管理
- 技能管理规范
- Git 操作规则

## 技能开发规范

### 创建新技能
```bash
python ~/.config/opencode/skills/skill-creator/scripts/create_skill.py <技能名> <描述>
```

### 更新技能版本
```bash
python ~/.config/opencode/skills/skill-creator/scripts/version_manager.py --skill <技能名> --bump <patch|minor|major> --message "变更描述"
```

## 许可证

本项目采用 [MIT License](./LICENSE) 开源许可证，允许自由使用、修改和分发，包括商业用途。
