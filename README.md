# WeCom for Mac Version Archive

Automated archive tracking and release repository for Tencent WeCom (Enterprise WeChat / 企业微信) macOS desktop clients.

[English](README.md) | [简体中文](README.zh-CN.md)

[![Release Latest WeCom Mac](https://github.com/meteor-ioi/wecom-mac-versions/actions/workflows/release.yml/badge.svg)](https://github.com/meteor-ioi/wecom-mac-versions/actions/workflows/release.yml)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/meteor-ioi/wecom-mac-versions/total)
![GitHub Downloads (all assets, latest release)](https://img.shields.io/github/downloads/meteor-ioi/wecom-mac-versions/latest/total)

This project uses `GitHub Actions` to automatically check for macOS client updates **every hour**, download official DMG packages for both **Apple Silicon** (M-series) and **Intel x86_64**, compute SHA-256 integrity checksums, and publish them together to the [Releases](https://github.com/meteor-ioi/wecom-mac-versions/releases) section.

It also supports chronologically backfilling historical releases. See [VERSIONS.md](VERSIONS.md) for the complete list of historical download links.

## Dual Architecture Support

Each release includes both architecture installers:
- **`WeCom_{version}_Apple.dmg`**: Native ARM64 build for Apple Silicon (M1/M2/M3/M4).
- **`WeCom_{version}_Intel.dmg`**: Native x86_64 build for Intel-based Macs.

## Related Projects

- [wecom-windows-versions](https://github.com/meteor-ioi/wecom-windows-versions) (WeCom Windows Version Archive)
- [WeChat Windows Version Archive](https://github.com/cscnk52/wechat-windows-versions) (by @cscnk52)
- [WeChat Mac 3.0 & 4.0 Archive](https://github.com/zsbai/wechat-versions) (by @zsbai)
- [WeChat Windows 64-bit 3.0 Archive](https://github.com/tom-snow/wechat-windows-versions) (by @tom-snow)

## How It Works

- **`.github/workflows/release.yml`**: Runs on a cron schedule (`0 * * * *`) and `workflow_dispatch`. Resolves official download redirection endpoints for both Apple Silicon and Intel, verifies updates, downloads DMG packages, hashes them, and publishes a new GitHub Release.
- **`.github/workflows/backfill.yml`**: Sequentially publishes historical versions from oldest to newest.
- **`versions.json`**: Verified historical versions dataset for Mac.

## License

This project is licensed under the [MIT License](./LICENSE). The installers belong to Tencent. This project is for archival and development reproduction purposes only.
