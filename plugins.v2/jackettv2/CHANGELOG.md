# JackettV2 插件更新日志

## v1.6.1 - 2024年最新版兼容性修正

### 🔧 修复内容

#### 1. **API兼容性修正**
- ✅ 添加了缺失的 `get_command()` 抽象方法
- ✅ 实现了远程命令支持：
  - `/jackett_reload` - 重新加载Jackett索引器
  - `/jackett_status` - 查看Jackett状态
- ✅ 添加了事件处理机制，支持通过消息命令控制插件

#### 2. **索引器集成策略优化**
- ✅ 改进了索引器添加方式，优先使用 `SitesHelper` API
- ✅ 实现了多级降级策略：
  - 主要方式：通过 SitesHelper 注册自定义站点
  - 备用方式：保存配置数据到插件数据库
- ✅ 增强了错误处理和兼容性检查

#### 3. **服务和调度优化**
- ✅ 添加了 `get_service()` 方法，实现定时同步功能
- ✅ 每6小时自动同步一次Jackett索引器
- ✅ 改进了插件生命周期管理

#### 4. **事件系统集成**
- ✅ 正确集成了 MoviePilot 的事件管理器
- ✅ 添加了命令处理器和状态查询功能
- ✅ 实现了消息推送通知功能

#### 5. **资源清理改进**
- ✅ 改进了插件停止时的资源清理
- ✅ 正确注销事件处理器
- ✅ 彻底清理添加的索引器配置

### 🚀 新功能

#### 远程控制命令
- **重新加载**: `/jackett_reload` - 立即重新加载所有Jackett索引器
- **状态查询**: `/jackett_status` - 查看插件当前状态和索引器数量

#### 自动同步
- 插件启用后每6小时自动同步一次索引器
- 支持新增、删除、更新Jackett中的索引器配置

#### 增强通知
- 操作结果会通过消息系统推送通知
- 详细的状态信息和错误提示

### 🔍 技术改进

#### API适配
```python
# 新增必需的抽象方法
def get_command(self) -> List[Dict[str, Any]]:
    # 注册远程命令

# 改进的索引器集成
def _add_jackett_indexers(self):
    # 使用SitesHelper API而非直接操作搜索链
```

#### 事件处理
```python
# 注册事件处理器
self.eventmanager.register("jackett.reload", self._handle_reload_command)
self.eventmanager.register("jackett.status", self._handle_status_command)

# 处理命令并发送通知
def _handle_reload_command(self, event: Event = None):
    # 执行操作并推送结果通知
```

### 🛠️ 兼容性

- ✅ **MoviePilot 最新版本**: 完全兼容
- ✅ **Python 3.12**: 支持最新Python版本
- ✅ **FastAPI**: 兼容最新FastAPI架构
- ✅ **Vue3前端**: 支持最新前端框架

### 📋 安装说明

1. 将插件文件放置到 MoviePilot 的 `plugins` 目录
2. 重启 MoviePilot 服务
3. 在插件管理中配置 Jackett 连接信息
4. 保存配置后插件将自动导入索引器

### ⚠️ 注意事项

- 确保 Jackett 服务正常运行且可访问
- API Key 必须正确配置
- 如果 Jackett 设置了管理密码，请在插件中正确配置
- 插件会自动处理索引器的增删改，无需手动干预

### 🔗 相关链接

- [MoviePilot 主项目](https://github.com/jxxghp/MoviePilot)
- [插件原始仓库](https://github.com/xj-bear/MoviePilot-Plugins)
- [MoviePilot Wiki](https://wiki.movie-pilot.org)