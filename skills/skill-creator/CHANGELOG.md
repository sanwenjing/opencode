# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-20

### Changed
- 更新许可信息为 MIT License，统一使用仓库根目录的 LICENSE 文件
- 移除技能目录结构中的 LICENSE.txt，不再创建单独的许可文件
- 更新 create_skill.py、skill_fixer.py、safe_fix.py、quick_fix.py 中的许可声明

## [1.3.0] - 2026-02-19

### Added
- 新增技能依赖声明功能，支持创建新技能时声明依赖其他已有技能

## [1.2.0] - 2026-02-18

### Added
- 新增config目录创建功能，创建新技能时自动创建config文件夹
- 新增config.example.json示例配置文件，用于展示配置项格式
- SKILL.md中添加配置文件目录说明和使用规范
- 创建流程中添加config目录验证清单

### Changed
- 更新目录结构说明，包含config目录
- 更新验证清单，添加config目录验证项
- 更新输出标准说明

## [1.1.0] - 2026-02-08

### Added
- 新增"技能修改规则"章节，规范技能修改时的版本号和CHANGELOG更新流程
- 添加版本号判断标准表格，明确MINOR和PATCH版本升级规则
- 添加CHANGELOG记录要求，包括变更分类（Added/Changed/Fixed/Verified）
- 添加技能修改自动流程，明确Claude必须执行的6个步骤
- 添加版本号判断示例表，帮助理解版本升级规则

## [1.3.0] - 2026-02-19

### Added
- 新增技能依赖声明功能，支持创建新技能时声明依赖其他已有技能
## [1.0.0] - 2026-02-08

### Added
- Initial release
