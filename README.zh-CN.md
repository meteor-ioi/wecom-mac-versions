# 企业微信 macOS 历史版本归档库 (WeCom for Mac Archive)

自动化追踪、下载并发布企业微信 (WeCom) macOS 桌面端历史版本的 GitHub 归档仓库。

[English](README.md) | [简体中文](README.zh-CN.md)

[![Release Latest WeCom Mac](https://github.com/meteor-ioi/wecom-mac-versions/actions/workflows/release.yml/badge.svg)](https://github.com/meteor-ioi/wecom-mac-versions/actions/workflows/release.yml)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/meteor-ioi/wecom-mac-versions/total)
![GitHub Downloads (all assets, latest release)](https://img.shields.io/github/downloads/meteor-ioi/wecom-mac-versions/latest/total)

本项目通过 `GitHub Actions` **每小时**自动检测腾讯企业微信官方分发服务器的 macOS 更新，自动拉取 **Apple Silicon (M系列)** 与 **Intel x86_64** 双架构 DMG 安装包、校验 SHA-256 哈希并同步发布至本仓库的 [Releases](https://github.com/meteor-ioi/wecom-mac-versions/releases) 页面。

## 双架构原生支持

每个发版均同时提供双端原生 DMG 安装包：
- **`WeCom_{version}_Apple.dmg`**：适用于搭载 M1/M2/M3/M4 系列芯片的 Mac 电脑。
- **`WeCom_{version}_Intel.dmg`**：适用于搭载 Intel 处理器的传统 Mac 电脑。

## 相关项目 (Related Projects)

- [wecom-windows-versions](https://github.com/meteor-ioi/wecom-windows-versions) (企业微信 Windows 版自动归档库)
- [WeChat Windows Version Archive](https://github.com/cscnk52/wechat-windows-versions) (by @cscnk52)
- [WeChat Mac 3.0 & 4.0 Archive](https://github.com/zsbai/wechat-versions) (by @zsbai)
- [WeChat Windows 64-bit 3.0 Archive](https://github.com/tom-snow/wechat-windows-versions) (by @tom-snow)

## 架构说明

- **`.github/workflows/release.yml`**：每小时整点定时巡检或手动触发。解析官方 `commdownload` 重定向端点嗅探最新客户端，若发现新版本则下载双架构包、计算 SHA-256 并发版（标记为 Latest）。
- **`.github/workflows/backfill.yml`**：历史版本批量回溯流。严格按**从旧到新（时间正序）**依次下载与发版，确保 Releases 列表中最老版本在底部、最新版本置顶。
- **`versions.json`**：收录并校验过的 Mac 历史版本及官方 CDN 下载源。

## 开源协议

本项目采用 [MIT 许可证](./LICENSE)。企业微信安装程序版权归腾讯公司所有，本项目仅供历史归档与研发兼容性测试之用。
