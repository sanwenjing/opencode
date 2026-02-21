# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2026-02-21

### Fixed
- 修复 `notification` 命令参数解析问题
- 支持多种调用方式：`notify`、`notification`、`-t title -c content`

### Changed
- 优化参数解析逻辑，支持从 args 中提取 -t/-c 参数

## [1.1.0] - 2026-02-20

### Added
- 新增 `notify` 子命令，专门用于发送通知
- 新增 `--title` 和 `--content` 参数，支持包含特殊字符的内容
- 新增 `escape_shell_arg` 函数，正确处理 shell 参数转义

### Fixed
- 修复通知内容包含特殊字符（换行、引号）时发送失败的问题

## [1.0.0] - 2026-02-19

### Added
- 初始版本发布
- 支持 45+ 个 Termux API 命令
- 封装 battery-status, info, torch, vibrate, clipboard, notification 等常用 API
- 依赖 remote-manager 技能执行远程命令
- 支持 list 命令查看所有可用 API
- 支持指定远程主机名
