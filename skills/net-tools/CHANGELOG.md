# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-22

### Added
- 扩展集成20+网络工具：
  - 连接测试：ping, traceroute, mtr
  - HTTP工具：curl, wget
  - 端口工具：nc, ss, netstat
  - DNS工具：dig, nslookup, host, whois
  - 抓包工具：tcpdump, ngrep
  - 带宽测试：iperf3
  - 网络配置：ip-addr, ip-route, ifconfig, route, arp
  - 远程连接：telnet, ftp
- Python socket fallback机制：当nmap不可用时自动使用socket扫描

### Fixed
- 修复nmap在受限环境下无法扫描的问题

## [1.0.0] - 2026-02-22

### Added
- 初始版本发布
- Nmap端口扫描功能（scan/quick/discover/service/os/full）
- 支持nmap和Python socket两种扫描方式
