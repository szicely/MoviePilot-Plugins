import os.path
from functools import lru_cache

from app.plugins import EventHandler
from app.plugins.modules._base import _IPluginModule
from app.indexer.indexerConf import IndexerConf
from app.utils import RequestUtils
from app.utils.types import MediaType, EventType
from app.utils import StringUtils
from config import Config
import log
from pyquery import PyQuery
from string import Template
import re
import json

class Btgpt(_IPluginModule):
    # 插件名称
    module_name = "Btgpt"
    # 插件描述
    module_desc = "BT资源搜索"
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
    module_config_prefix = "btgptindexer_"
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
    _indexer = {
            "id": "Btgpt",
            "name": "Btgpt",
            "domain": "https://so.btgpt.net/",
            "encoding": "UTF-8",
            "parser": "Btgpt",
            "public": True,
            "proxy": True,
            "language": "zh"
        }
    _req = None
    _base_url = "https://so.btgpt.net/"
    _search_url = "https://so.btgpt.net/api/"
    _indexer_id = "Btgpt"

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
        return []

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

    def search(self, *args, **kwargs):
        torrents = []
        log.info(str(kwargs))
        log.warn(f"【Indexer】信息：{self._indexer_id} https://so.btgpt.net/api/")
        post_data = {
            "kw": kwargs["keyword"],
            "page": 1
        }
        res = self._req.post(url=self._search_url, data=post_data)
        if not res or res.status_code != 200:
            return torrents
        # print(res.content.decode("UTF-8"))
        json_doc = json.loads(res.content)
        if "code" not in json_doc or 1 != json_doc["code"]:
            return torrents
        data_list = json_doc["data"]
        for sub_t in data_list:
            title = sub_t["title"]
            enclosure = sub_t["url"]
            size = StringUtils.num_filesize(sub_t["size"].strip())
            seeders = ""
            peers = ""
            # date = sub_t["date"]
            page_url = self._base_url
            torrent = {'indexer': self._indexer_id,
                        'title': title,
                        'enclosure': enclosure,
                        'size': size,
                        'seeders': seeders,
                        'peers': peers,
                        'freeleech': True,
                        'downloadvolumefactor': 0.0,
                        'uploadvolumefactor': 1.0,
                        'page_url': page_url,
                        'imdbid': ""}
            torrents.append(torrent)
            # log.info(str(torrent))
        return torrents

