# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.0] - 2026-02-20

### Fixed
- 修复手机通知发送失败问题，使用 termux-api-controller 的 notify 子命令
- 正确处理通知内容中的特殊字符（换行、引号等）

### Changed
- 更新依赖 termux-api-controller 最低版本为 1.1.0

## [0.6.0] - 2026-02-20

### Changed
- 失败时不再发送通知，仅记录日志，避免频繁打扰
- 优化错误处理流程

## [0.5.0] - 2026-02-20

### Added
- 新增手机通知功能，通过 termux-api-controller 技能发送
- 同时发送邮件和手机通知，防止邮件被拦截
- 新增依赖 termux-api-controller 技能

### Changed
- 优化通知机制，邮件和手机双重通知

## [0.4.1] - 2026-02-19

### Added
- 新增push前检查是否有需要推送的内容

## [0.4.0] - 2026-02-19

### Changed
- 修改为依赖email-sender技能发送邮件通知

## [0.2.0] - 2026-02-19

### Changed
- 增加git push自动重试功能，最多重试30分钟

## [0.1.1] - 2026-02-19

### Fixed
- 修复版本管理器路径硬编码问题

## [0.1.0] - 2026-02-18

### Added
- 新增 --repo/-r 参数，支持指定仓库文件夹路径，默认 ~/.config/opencode
- 使用 subprocess cwd 参数执行 git push，保持当前目录不变
