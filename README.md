# BT资源搜索器

一个基于Python的BT资源搜索器集合，支持多个BT站点的资源搜索和下载。

## 功能特点

- 🔍 **多站点支持** - 支持多个BT站点搜索
- 📄 **分页搜索** - 支持最多20页搜索，每页20个结果
- 🎯 **智能过滤** - 关键字匹配和相关性过滤
- 🔗 **多链接格式** - 支持磁力链接、种子文件等多种下载方式
- 📊 **详细日志** - 完整的搜索过程记录和统计

## 技术栈

- **语言**: Python 3.x
- **HTML解析**: PyQuery
- **HTTP请求**: RequestUtils
- **网页爬虫**: 自定义爬虫框架

## 支持的站点

- ✅ **BT之家** (1lou.me) - 完全支持，分页搜索
- ✅ **其他站点** - 多个备用搜索器

## 安装使用

1. 克隆项目
```bash
git clone https://github.com/你的用户名/bt-searcher.git
cd bt-searcher
```

2. 安装依赖
```bash
pip install pyquery requests
```

3. 运行搜索器
```python
from btzjindexer import Btzj

# 创建搜索器实例
searcher = Btzj()
searcher.init_config()

# 搜索资源
results = searcher.search(keyword="关键字")
print(f"找到 {len(results)} 个结果")
```

## 配置说明

### 分页配置
- `_max_pages = 20` - 最大搜索页数
- `_max_results_per_page = 20` - 每页处理结果数
- 理论最大结果数：400条

### URL格式
- 第1页：`https://www.1lou.me/search-bt{keyword}.htm`
- 其他页：`https://www.1lou.me/search-bt_{encoded_keyword}-1-{page}.htm`

## 项目结构

```
├── btzjindexer.py      # BT之家搜索器
├── btgptindexer.py     # GPT站搜索器
├── btttindexer.py      # BT天堂搜索器
├── .gitignore          # Git忽略文件
└── README.md           # 项目说明
```

## 更新日志

### v1.1 (最新)
- ✅ 修正分页URL格式问题
- ✅ 更新域名为 www.1lou.me
- ✅ 优化分页配置：20页 × 20结果
- ✅ 增强错误处理和日志记录

### v1.0
- ✅ 基础搜索功能
- ✅ 多站点支持
- ✅ 结果过滤和标准化

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License