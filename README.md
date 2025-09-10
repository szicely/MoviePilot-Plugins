# MoviePilot-Plugins

这是一个为 [MoviePilot](https://github.com/jxxghp/MoviePilot) 项目开发的第三方插件仓库。

## 📖 项目介绍

MoviePilot 是一个媒体库自动化管理工具，聚焦自动化核心需求，减少问题同时更易于扩展和维护。本仓库提供了实用的第三方插件，用于扩展 MoviePilot 的功能。

## 🔌 插件列表

### V2 版本插件

#### 🔍 JackettV2 - Jackett 搜索器插件
- **版本**: v1.6.1
- **作者**: jason (原作者) + szicely (兼容性修正)
- **描述**: 支持 Jackett 搜索器，将 Jackett 索引器添加到 MoviePilot V2 内建搜索器中
- **路径**: `plugins.v2/jackettv2/`

**主要功能**:
- ✅ 自动集成 Jackett 中配置的索引器到 MoviePilot 搜索系统
- ✅ 支持选择性导入指定的索引器
- ✅ 提供 RESTful API 用于管理索引器
- ✅ 支持远程命令控制（`/jackett_reload`, `/jackett_status`）
- ✅ 自动定时同步（每6小时）
- ✅ 完整的错误处理和日志记录

**兼容性**:
- ✅ MoviePilot >= 2.0.0
- ✅ Python >= 3.12
- ✅ 已修复与最新版 MoviePilot 的兼容性问题


## 📝 更新日志

### 2024-09-10
- 🆕 创建仓库
- ✅ 添加 JackettV2 插件 v1.6.1
- 🔧 修复 JackettV2 与 MoviePilot 最新版本的兼容性问题
- 📚 完善文档和部署指南

## ⚠️ 免责声明

- 本项目仅供学习交流使用，请勿用于商业用途
- 插件的使用风险由用户自行承担
- 请遵守相关法律法规和网站的使用条款

## 🔗 相关链接

- [MoviePilot 主项目](https://github.com/jxxghp/MoviePilot)
- [MoviePilot 官方插件](https://github.com/jxxghp/MoviePilot-Plugins)
- [MoviePilot Wiki](https://wiki.movie-pilot.org)
- [MoviePilot API 文档](https://api.movie-pilot.org)

## 📄 开源协议

本项目基于 MIT 协议开源。
