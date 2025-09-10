# 🚀 JackettV2 插件快速部署指南

## 📋 部署步骤

### 1. 停止 MoviePilot 服务
```bash
# Docker 用户
docker-compose down

# 或者
docker stop moviepilot

# 直接运行用户
# 停止正在运行的 MoviePilot 进程
```

### 2. 部署插件文件
将整个 `jackettv2` 文件夹复制到 MoviePilot 的插件目录：

```
MoviePilot/
├── app/
│   └── plugins/
│       └── jackettv2/          # 将插件文件夹放在这里
│           ├── __init__.py
│           ├── README.md
│           ├── plugin.json
│           └── CHANGELOG.md
```

### 3. 启动 MoviePilot 服务
```bash
# Docker 用户
docker-compose up -d

# 或者
docker start moviepilot

# 直接运行用户
python3 main.py
```

### 4. 配置插件

1. 打开 MoviePilot Web 界面
2. 进入 **插件管理** 页面
3. 找到 **JackettV2** 插件
4. 点击 **配置** 按钮
5. 填写以下信息：
   - **启用插件**: ✅ 开启
   - **Jackett地址**: `http://your-jackett-ip:9117`
   - **API Key**: 从 Jackett 管理界面复制
   - **管理密码**: 如果设置了的话
   - **索引器**: 留空使用全部，或选择特定索引器

### 5. 验证部署

#### 方法1: 查看日志
```bash
# Docker 用户查看日志
docker logs moviepilot

# 直接运行用户查看控制台输出
```

看到类似信息说明部署成功：
```
【JackettV2】正在初始化插件...
【JackettV2】插件初始化完成，状态: True
【JackettV2】尝试添加Jackett索引器...
【JackettV2】成功获取到5个索引器
【JackettV2】成功添加索引器: 1337x
【JackettV2】共添加了 5 个Jackett索引器
```

#### 方法2: 使用远程命令
在配置的消息渠道（微信/Telegram等）中发送：
```
/jackett_status
```

#### 方法3: 检查API
访问: `http://your-moviepilot:3001/api/v1/plugin/jackettv2/indexers`

## 🛠️ 故障排除

### 常见问题

1. **插件无法加载**
   - 检查文件权限是否正确
   - 确认 Python 版本 >= 3.12
   - 查看 MoviePilot 日志中的错误信息

2. **无法获取索引器**
   - 验证 Jackett 地址是否可访问
   - 检查 API Key 是否正确
   - 确认 Jackett 服务正常运行

3. **索引器未显示在搜索中**
   - 重启 MoviePilot 服务
   - 使用 `/jackett_reload` 命令重新加载
   - 检查插件日志中的错误信息

### 日志位置

- **Docker**: `docker logs moviepilot`
- **直接运行**: 控制台输出
- **插件日志**: MoviePilot Web界面 → 日志页面

## 🔄 更新插件

1. 停止 MoviePilot 服务
2. 替换插件文件
3. 重启 MoviePilot 服务
4. 插件会自动重新初始化

## ⚙️ 高级配置

### 自定义同步间隔
插件默认每6小时同步一次索引器。如需修改：

1. 编辑 `__init__.py` 文件
2. 找到 `get_service()` 方法
3. 修改 `"kwargs": {"hours": 6}` 中的数值

### 选择性导入索引器
在插件配置中的"索引器"选项中选择特定的索引器ID，而不是留空导入全部。

## 📞 技术支持

- 查看 [CHANGELOG.md](./CHANGELOG.md) 了解最新变更
- 查看 [README.md](./README.md) 了解详细功能
- 原项目地址: https://github.com/xj-bear/MoviePilot-Plugins
- MoviePilot 官方: https://github.com/jxxghp/MoviePilot