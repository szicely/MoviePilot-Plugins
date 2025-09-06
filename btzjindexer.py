import os.path
from functools import lru_cache

from app.plugins import EventHandler
from app.plugins.modules._base import _IPluginModule
from app.indexer.indexerConf import IndexerConf
from app.utils import RequestUtils
from app.utils.types import MediaType, EventType
from config import Config
import log
from pyquery import PyQuery
from string import Template
import re

class Btzj(_IPluginModule):
    # 插件名称
    module_name = "Btzj"
    # 插件描述
    module_desc = "BT之家搜索器"
    # 插件图标
    module_icon = "chinesesubfinder.png"
    # 主题色
    module_color = "#83BE39"
    # 插件版本
    module_version = "1.0"
    # 插件作者
    module_author = "me"
    # 作者主页
    author_url = "https://github.com/PterX/nas-tools-plugins"
    # 插件配置项ID前缀
    module_config_prefix = "btzjindexer_"
    # 加载顺序
    module_order = 3
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _save_tmp_path = None
    _host = None
    _api_key = None
    _remote_path = None
    _local_path = None
    _remote_path2 = None
    _local_path2 = None
    _remote_path3 = None
    _local_path3 = None
    # 分页配置
    _max_pages = 20  # 默认搜索20页
    _max_results_per_page = 20  # 每页最多处理20个结果
    _indexer = {
            "id": "Btzj",
            "name": "Btzj",
            "domain": "https://1lou.me/",
            "encoding": "UTF-8",
            "parser": "Btzj",
            "public": True,
            "proxy": True,
            "language": "zh"
        }
    _req = None
    _base_url = "https://1lou.me/"
    _indexer_id = "Btzj"

    def init_config(self, config: dict = None):
        self._save_tmp_path = Config().get_temp_path()
        if not os.path.exists(self._save_tmp_path):
            os.makedirs(self._save_tmp_path)
        import requests
        session = requests.session()
        self._req = RequestUtils(proxies=Config().get_proxies(), session=session, timeout=10)

    def get_state(self):
        return True

    @staticmethod
    def get_fields():
        return [
            # 可以添加分页配置字段
            # {
            #     'type': 'number',
            #     'id': 'max_pages',
            #     'name': '最大搜索页数',
            #     'default': 3,
            #     'tooltip': '最多搜索多少页结果，默认3页'
            # },
            # {
            #     'type': 'number',
            #     'id': 'max_results_per_page',
            #     'name': '每页最大结果数',
            #     'default': 10,
            #     'tooltip': '每页最多处理多少个结果，默认10个'
            # }
        ]

    def stop_service(self):
        pass

    def get_indexers(self):
        return [IndexerConf(datas=self._indexer,
                           siteid=self._indexer_id)]

    def _text(self, item):
        if not item:
            return ""
        return item.text()
    
    def _attr(self, item, attr):
        if not item:
            return ""
        return item.attr(attr)

        # 构造搜索 URL
    def search(self, *args, **kwargs):
        torrents = []
        keyword = kwargs["keyword"]
        
        # 分页配置
        max_pages = self._max_pages  # 使用类属性
        
        log.warn(f"【Indexer】信息：{self._indexer_id} 开始分页搜索，关键字: {keyword}，最多{max_pages}页")
        
        # 对关键字进行URL编码（模拟浏览器格式）
        import urllib.parse
        encoded_keyword = urllib.parse.quote(keyword, safe='').replace('%', '_')
        
        # 遍历多个页面
        current_page = 0
        for page in range(1, max_pages + 1):
            current_page = page
            if page == 1:
                search_url = f"https://www.1lou.me/search-bt{keyword}.htm"
            else:
                # 使用浏览器实际的分页URL格式
                search_url = f"https://www.1lou.me/search-bt_{encoded_keyword}-1-{page}.htm"
                
            log.warn(f"【Indexer】信息：搜索第{page}页 - {search_url}")
            
            # 发送搜索请求
            res = self._req.get_res(url=search_url)
            if not res or res.status_code != 200:
                log.warn(f"【Indexer】信息：第{page}页请求失败，状态码: {res.status_code if res else 'None'}")
                continue
                
            page_torrents = self._parse_search_page(res, keyword, page)
            torrents.extend(page_torrents)
            
            # 如果当前页没有找到结果，可能已经到了最后一页
            if not page_torrents:
                log.warn(f"【Indexer】信息：第{page}页无结果，停止搜索")
                break
                
        log.warn(f"【Indexer】信息：分页搜索完成，共搜索{current_page}页，找到{len(torrents)}个有效结果")
        return torrents
    
    def _parse_search_page(self, res, keyword, page_num):
        """解析单个搜索结果页面"""
        torrents = []
        
        log.warn(f"【Indexer】信息：第{page_num}页请求成功，开始解析")
        # print(res.content.decode("UTF-8"))
        
        # 解析搜索结果 - 更新选择器以适应新的HTML结构
        html_doc = PyQuery(res.content)
        
        # 尝试多种可能的选择器
        # 新版本的网站结构可能使用了不同的CSS类
        sub_urls = []
        
        # 选择器1: 优先使用包含thread-的链接（获取所有结果）
        potential_links = html_doc("a[href*='thread-']")
        if potential_links:
            sub_urls = potential_links
            log.warn(f"【Indexer】信息：第{page_num}页使用thread-选择器找到 {len(sub_urls)} 个结果")
        
        # 如果没找到，尝试其他选择器
        if not sub_urls:
            potential_links = html_doc("a[href*='.html']")
            if potential_links:
                sub_urls = potential_links
                log.warn(f"【Indexer】信息：第{page_num}页使用链接选择器找到 {len(sub_urls)} 个结果")
        
        # 如果还是没找到，尝试更广泛的搜索
        if not sub_urls:
            potential_links = html_doc("a").filter(lambda i, e: 'BT下载' in PyQuery(e).text() or '下载' in PyQuery(e).text())
            if potential_links:
                sub_urls = potential_links
                log.warn(f"【Indexer】信息：第{page_num}页使用下载文本选择器找到 {len(sub_urls)} 个结果")
        
        if not sub_urls:
            log.warn(f"【Indexer】信息：第{page_num}页未找到任何有效的种子链接")
            return torrents
        
        processed_count = 0
        max_results_per_page = self._max_results_per_page  # 使用类属性
        
        # 遍历每个种子链接
        for sub_t in sub_urls[:max_results_per_page]:
            sub_item = PyQuery(sub_t)
            title = self._text(sub_item).strip()
            
            # 过滤掉明显不是资源的链接
            if not title or len(title) < 3:
                continue
            if any(skip_word in title.lower() for skip_word in ['登录', '注册', '首页', '搜索', '分类']):
                continue
            
            # 检查是否包含关键字（必须过滤）
            if keyword.lower() not in title.lower():
                continue
                
            log.warn(f"【Indexer】信息：第{page_num}页找到种子标题 - {title}")
                
            # 获取详情页链接    
            detail_sub = self._attr(sub_item, "href")
            if not detail_sub:
                log.warn(f"【Indexer】信息：错误：未找到详情页链接")
                continue
                
            if not detail_sub.startswith("http://") and not detail_sub.startswith("https://"):
                if detail_sub.startswith("/"):
                    detail_sub = "https://www.1lou.me" + detail_sub
                else:
                    detail_sub = "https://www.1lou.me/" + detail_sub
                    
            log.warn(f"【Indexer】信息：详情页链接 - {detail_sub}")
                
        
            # 发送详情页请求
            detail_ret = self._req.get_res(url=detail_sub)
            if not detail_ret or detail_ret.status_code != 200:
                continue
        
            # 解析详情页，获取下载链接
            detail_doc = PyQuery(detail_ret.content)
            
            # 尝试多种下载链接选择器
            enclosure = None
            
            # 选择器1: 寻找包含attach-download的链接
            enclosure = self._attr(detail_doc("a[href*='attach-download']"), "href")
            
            # 选择器2: 寻找包含.torrent的链接
            if not enclosure:
                enclosure = self._attr(detail_doc("a[href*='.torrent']"), "href")
            
            # 选择器3: 寻找包含download的链接
            if not enclosure:
                enclosure = self._attr(detail_doc("a[href*='download']"), "href")
                
            # 选择器4: 寻找magnet链接
            if not enclosure:
                enclosure = self._attr(detail_doc("a[href^='magnet:']"), "href")
            
            if not enclosure:
                log.warn(f"【Indexer】信息：错误：未找到下载链接 - {detail_sub}")
                continue
                
            # 处理相对URL
            if enclosure and not enclosure.startswith(("http://", "https://", "magnet:")):
                if enclosure.startswith("/"):
                    enclosure = "https://www.1lou.me" + enclosure
                else:
                    enclosure = "https://www.1lou.me/" + enclosure
                    
            log.warn(f"【Indexer】信息：下载链接 - {enclosure}")
                
            # 构造种子信息
            torrent = {'indexer': self._indexer_id,
                       'title': title,
                       'enclosure': enclosure,
                       'size': "",
                       'seeders': "",
                       'peers': "",
                       'freeleech': True,
                       'downloadvolumefactor': 0.0,
                       'uploadvolumefactor': 1.0,
                       'page_url': detail_sub,
                       'imdbid': ""}
            torrents.append(torrent)
            processed_count += 1
            
        log.warn(f"【Indexer】信息：第{page_num}页处理完成，处理 {processed_count} 个种子，返回 {len(torrents)} 个有效结果")
        return torrents

