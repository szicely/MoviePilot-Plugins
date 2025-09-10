# JackettV2 插件

这是一个为 MoviePilot V2 版本设计的 Jackett 搜索器插件。**已修复与最新版MoviePilot的兼容性问题**。

## ✨ 最新更新 (v1.6.1)

- 🔧 **修复兼容性**: 解决了与MoviePilot最新版本的API兼容性问题
- 🎯 **新增远程控制**: 支持通过消息命令远程控制插件
- ⚡ **自动同步**: 每6小时自动同步Jackett索引器
- 🛡️ **增强稳定性**: 改进错误处理和资源清理机制

## 功能说明

- 支持将 Jackett 中配置的索引器添加到 MoviePilot V2 的内建搜索器中
- 自动获取 Jackett 中已配置的索引器列表
- 支持选择性导入指定的索引器
- 提供 API 接口用于管理索引器

## 配置说明

### 基本配置

1. **启用插件**: 开启或关闭插件功能
2. **Jackett地址**: Jackett 服务的完整地址，例如 `http://localhost:9117`
3. **API Key**: 在 Jackett 管理界面右上角可以找到的 API Key
4. **管理密码**: 如果 Jackett 设置了 Admin password，需要填写此项
5. **索引器**: 可以选择要导入的特定索引器，留空则导入全部

### 使用步骤

1. 确保 Jackett 服务正常运行
2. 在 Jackett 中配置好需要的索引器
3. 在 MoviePilot 插件管理中安装并配置此插件
4. 填写正确的 Jackett 地址和 API Key
5. 保存配置后，插件会自动导入 Jackett 中的索引器

## 🎮 远程控制命令

插件现在支持通过消息系统远程控制：

- **`/jackett_reload`** - 重新加载Jackett索引器
- **`/jackett_status`** - 查看插件和索引器状态

可以在微信、Telegram或其他配置的消息渠道中使用这些命令。

## API 接口

### 获取索引器列表
```
GET /api/v1/plugin/jackettv2/indexers
```

### 重新加载索引器
```
GET /api/v1/plugin/jackettv2/reload
```

## 注意事项

1. 请确保 Jackett 服务可以正常访问
2. API Key 必须正确，否则无法获取索引器列表
3. 如果 Jackett 设置了管理密码，必须在插件中配置
4. 插件会自动处理之前添加的索引器，避免重复添加

## 版本历史

- **v1.6.1**: 修复与MoviePilot最新版本的兼容性问题，添加远程命令和自动同步功能
- **v1.6**: 原始版本，支持 MoviePilot V2
- 作者: jason
- 项目地址: https://github.com/xj-bear/MoviePilot-Plugins

## 故障排除

如果遇到问题，可以查看 MoviePilot 的日志输出，插件会输出详细的调试信息。

常见问题：
1. 无法获取索引器 - 检查 Jackett 地址和 API Key 是否正确
2. 认证失败 - 检查管理密码是否设置正确
3. 索引器不工作 - 确保 Jackett 中的索引器配置正常