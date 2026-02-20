# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-02-20

### Added
- 新增发送日志功能，记录发送时间、收件人、主题、正文、发送结果
- 日志文件保存为 email_send_log.json
- 支持使用配置文件中的 default_to 作为默认收件人

### Fixed
- 修复不传 -t 参数时无法使用 default_to 配置的问题

## [1.2.0] - 2026-02-18

### Added
- 新增config目录，用于存放配置文件
- 新增config.example.json配置文件示例

### Changed
- 更新目录结构说明，包含config目录
- 更新验证清单，添加config目录验证项

## [1.1.0] - 2026-02-18

### Added
- 邮件发送功能：支持自动生成主题、配置文件管理账号信息
- 文件附件发送功能
- 文件夹自动打包成ZIP后发送功能
- 完整的命令行参数支持
- 配置文件JSON格式，支持SMTP服务器、端口、SSL/TLS、账号密码等设置
- 支持Gmail、QQ邮箱、企业邮箱等多种邮件服务商

### Verified
- 验证环境：Python 3.x (Linux)
