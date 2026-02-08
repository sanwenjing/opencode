# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-08

### Added
- 新增安装版本信息表（Node.js v24.13.0, npm 11.6.3, OpenCode 1.1.53）

### Changed
- 改用Alpine apk包管理器安装Node.js和npm（替代手动下载tar.xz方式）
- 更新部署流程，简化安装步骤
- 更新符号链接路径（/usr/local/lib/node_modules/opencode-ai/...）
- 返回值新增 `npm_version` 字段

### Verified
- 在 server-2222 (192.168.31.150:2222) Alpine 3.23 验证成功

## [1.0.0] - 2026-02-08

### Added
- 初始版本发布
- 基础OpenCode部署功能
- 支持SSH连接管理
- 支持批量命令执行
- 支持数据导入导出
