# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-02-08

### Fixed
- 修复exec命令参数冲突bug
## [1.0.0] - 2026-02-08

### Added
- 初始版本发布
- 主机管理功能（添加、删除、更新、列出主机）
- 批量命令执行功能（SSH远程执行命令）
- CSV导入导出功能
- 主机信息持久化存储（hosts.yaml）
- 支持密码和私钥两种SSH认证方式
- 新增操作系统版本自动获取功能
- 新增refresh命令刷新操作系统版本
- 新增操作系统列在主机列表中显示
