from typing import Dict, Any, List, Optional, Tuple
from app.plugins import _PluginBase
from app.utils.http import RequestUtils
from app.schemas import NotificationType
try:
    from app.core.event import eventmanager, Event
except ImportError:
    # 兼容不同版本的MoviePilot
    eventmanager = None
    Event = None
import json
import os
import time
import xml.dom.minidom
from urllib.parse import urljoin
import requests

class JackettV2(_PluginBase):
    """
    Jackett V2 搜索器插件 - 专为MoviePilot V2版本设计
    """
    # 插件名称
    plugin_name = "JackettV2"
    # 插件描述
    plugin_desc = "支持 Jackett 搜索器，将Jackett索引器添加到MoviePilot V2内建搜索器中。"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/Jackett/Jackett/master/src/Jackett.Common/Content/favicon.ico"
    # 插件版本
    plugin_version = "1.6.1"
    # 插件作者
    plugin_author = "jason"
    # 作者主页  
    author_url = "https://github.com/szicely"
    # 插件配置项ID前缀
    plugin_config_prefix = "jackettv2_"
    # 加载顺序
    plugin_order = 21
    # 可使用的用户级别
    user_level = 2

    # 私有属性
    _enabled = False
    _host = None
    _api_key = None
    _password = None
    _indexers = None
    _added_indexers = []
    # 会话信息
    _session = None
    _cookies = None

    def init_plugin(self, config: dict = None) -> None:
        """
        插件初始化
        """
        try:
            print(f"【{self.plugin_name}】正在初始化插件...")
            if not config:
                print(f"【{self.plugin_name}】配置为空")
                return

            # 读取配置
            self._enabled = config.get("enabled", False)
            self._host = config.get("host")
            self._api_key = config.get("api_key")
            self._password = config.get("password")
            self._indexers = config.get("indexers", [])
            
            # 初始化会话
            self._session = None
            self._cookies = None
            
            # 注册事件处理器（兼容处理）
            try:
                if hasattr(self, 'eventmanager') and self.eventmanager:
                    self.eventmanager.register("jackett.reload", self._handle_reload_command)
                    self.eventmanager.register("jackett.status", self._handle_status_command)
                elif eventmanager:
                    eventmanager.register("jackett.reload", self._handle_reload_command)
                    eventmanager.register("jackett.status", self._handle_status_command)
            except Exception as e:
                print(f"【{self.plugin_name}】事件管理器注册失败: {str(e)}")
            
            print(f"【{self.plugin_name}】插件初始化完成，状态: {self._enabled}")
            
            # 如果配置了API信息，则尝试添加索引器，即使插件未启用
            if self._host and self._api_key:
                print(f"【{self.plugin_name}】尝试添加Jackett索引器...")
                try:
                    self._add_jackett_indexers()
                except Exception as e:
                    print(f"【{self.plugin_name}】添加索引器异常: {str(e)}")
                    import traceback
                    print(f"【{self.plugin_name}】异常详情: {traceback.format_exc()}")
        except Exception as e:
            print(f"【{self.plugin_name}】插件初始化失败: {str(e)}")
            import traceback
            print(f"【{self.plugin_name}】初始化异常详情: {traceback.format_exc()}")

    def _handle_reload_command(self, event: Event = None):
        """
        处理重新加载命令
        """
        try:
            result = self.reload_indexers()
            message = result.get("message", "重新加载完成")
            self.post_message(
                mtype=NotificationType.Plugin,
                title=f"【{self.plugin_name}】",
                text=message
            )
        except Exception as e:
            self.post_message(
                mtype=NotificationType.Plugin,
                title=f"【{self.plugin_name}】",
                text=f"重新加载失败: {str(e)}"
            )

    def _handle_status_command(self, event: Event = None):
        """
        处理状态查询命令
        """
        try:
            indexers = self._fetch_jackett_indexers()
            status_text = f"插件状态: {'启用' if self._enabled else '禁用'}\n"
            status_text += f"Jackett地址: {self._host or '未配置'}\n"
            status_text += f"API Key: {'已配置' if self._api_key else '未配置'}\n"
            status_text += f"可用索引器: {len(indexers)}个\n"
            status_text += f"已添加索引器: {len(self._added_indexers)}个"
            
            self.post_message(
                mtype=NotificationType.Plugin,
                title=f"【{self.plugin_name}】状态",
                text=status_text
            )
        except Exception as e:
            self.post_message(
                mtype=NotificationType.Plugin,
                title=f"【{self.plugin_name}】",
                text=f"状态查询失败: {str(e)}"
            )

    def get_state(self) -> bool:
        """
        获取插件状态
        """
        try:
            state = bool(self._enabled and self._host and self._api_key)
            print(f"【{self.plugin_name}】get_state返回: {state}, enabled={self._enabled}, host={bool(self._host)}, api_key={bool(self._api_key)}")
            return state
        except Exception as e:
            print(f"【{self.plugin_name}】get_state异常: {str(e)}")
            return False

    def get_command(self) -> List[Dict[str, Any]]:
        """
        注册插件远程命令
        """
        return [
            {
                "cmd": "/jackett_reload",
                "event": "jackett.reload",
                "desc": "重新加载Jackett索引器",
                "category": "Jackett",
                "data": {}
            },
            {
                "cmd": "/jackett_status",
                "event": "jackett.status",
                "desc": "查看Jackett状态",
                "category": "Jackett",
                "data": {}
            }
        ]

    def get_form(self) -> Tuple[List[dict], dict]:
        """
        获取配置表单
        """
        return [
            {
                'component': 'VAlert',
                'props': {
                    'type': 'info',
                    'text': '配置Jackett服务器信息后，将自动导入Jackett中配置的索引器到MoviePilot搜索系统。请确保Jackett服务可以正常访问，并且已经配置了可用的索引器。',
                    'class': 'mb-4'
                }
            },
            {
                'component': 'VSwitch',
                'props': {
                    'model': 'enabled',
                    'label': '启用插件'
                }
            },
            {
                'component': 'VTextField',
                'props': {
                    'model': 'host',
                    'label': 'Jackett地址',
                    'placeholder': 'http://localhost:9117',
                    'hint': '请输入Jackett的完整地址，包括http或https前缀，不要以斜杠结尾'
                }
            },
            {
                'component': 'VTextField',
                'props': {
                    'model': 'api_key',
                    'label': 'API Key',
                    'type': 'password',
                    'placeholder': 'Jackett管理界面右上角的API Key'
                }
            },
            {
                'component': 'VTextField',
                'props': {
                    'model': 'password',
                    'label': '管理密码',
                    'type': 'password',
                    'placeholder': 'Jackett管理界面配置的Admin password，如未配置可为空'
                }
            },
            {
                'component': 'VSelect',
                'props': {
                    'model': 'indexers',
                    'label': '索引器',
                    'multiple': True,
                    'chips': True,
                    'items': [],
                    'hint': '留空则使用全部索引器，获取索引器前需保存基本配置'
                }
            }
        ], {
            "enabled": False,
            "host": "",
            "api_key": "",
            "password": "",
            "indexers": []
        }

    def get_page(self) -> List[dict]:
        """
        获取页面
        """
        return [
            {
                'component': 'VAlert',
                'props': {
                    'type': 'info',
                    'text': '此插件用于对接Jackett搜索器，将Jackett中配置的索引器添加到MoviePilot的内建索引中。需要先在Jackett中添加并配置好索引器，启用插件并保存配置后，即可在搜索中使用这些索引器。',
                    'class': 'mb-4'
                }
            }
        ]

    def get_api(self) -> List[dict]:
        """
        获取API接口
        """
        return [
            {
                "path": "/jackettv2/indexers",
                "endpoint": self.get_indexers,
                "methods": ["GET"],
                "summary": "获取Jackett索引器列表",
                "description": "获取已配置的Jackett索引器列表"
            },
            {
                "path": "/jackettv2/reload",
                "endpoint": self.reload_indexers,
                "methods": ["GET"],
                "summary": "重新加载Jackett索引器",
                "description": "重新加载Jackett索引器到MoviePilot"
            }
        ]

    def _fetch_jackett_indexers(self):
        """
        获取Jackett索引器列表
        """
        if not self._host or not self._api_key:
            print(f"【{self.plugin_name}】缺少必要配置参数，无法获取索引器")
            return []
        
        # 规范化host地址
        if self._host.endswith('/'):
            self._host = self._host[:-1]
            
        try:
            # 设置请求头
            headers = {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "User-Agent": "MoviePilot/2.0",
                "X-Api-Key": self._api_key,
                "Accept": "application/json, text/javascript, */*; q=0.01"
            }
            
            # 创建session并设置headers
            session = requests.session()
            req = RequestUtils(headers=headers, session=session)
            
            # 如果设置了密码，则进行认证
            if self._password:
                dashboard_url = f"{self._host}/UI/Dashboard"
                auth_data = {"password": self._password}
                auth_params = {"password": self._password}
                
                dashboard_res = req.post_res(
                    url=dashboard_url,
                    data=auth_data,
                    params=auth_params
                )
                
                if dashboard_res and session.cookies:
                    self._cookies = session.cookies.get_dict()
            
            # 获取索引器列表
            indexer_query_url = f"{self._host}/api/v2.0/indexers?configured=true"
            response = req.get_res(
                url=indexer_query_url,
                verify=False
            )
            
            if response and response.status_code == 200:
                indexers = response.json()
                if indexers and isinstance(indexers, list):
                    print(f"【{self.plugin_name}】成功获取到{len(indexers)}个索引器")
                    return indexers
                    
            return []
                
        except Exception as e:
            print(f"【{self.plugin_name}】获取Jackett索引器异常: {str(e)}")
            return []

    def _format_indexer(self, jackett_indexer):
        """
        将Jackett索引器格式化为MoviePilot V2索引器格式
        """
        try:
            # 从Jackett API返回的数据中提取必要信息
            indexer_id = jackett_indexer.get("id", "")
            indexer_name = jackett_indexer.get("name", "")
            
            # 添加分类信息
            categories = {
                "movie": [
                    {"id": "2000", "desc": "Movies"}, 
                    {"id": "2010", "desc": "Movies/Foreign"},
                    {"id": "2020", "desc": "Movies/BluRay"}, 
                    {"id": "2030", "desc": "Movies/DVD"},
                    {"id": "2040", "desc": "Movies/HD"}, 
                    {"id": "2045", "desc": "Movies/UHD"},
                    {"id": "2050", "desc": "Movies/3D"}, 
                    {"id": "2060", "desc": "Movies/SD"}
                ],
                "tv": [
                    {"id": "5000", "desc": "TV"}, 
                    {"id": "5020", "desc": "TV/Blu-ray"},
                    {"id": "5030", "desc": "TV/DVD"}, 
                    {"id": "5040", "desc": "TV/HD"},
                    {"id": "5050", "desc": "TV/SD"}, 
                    {"id": "5060", "desc": "TV/Foreign"},
                    {"id": "5070", "desc": "TV/Sport"}
                ]
            }
            
            # 构建索引器配置
            indexer_config = {
                "id": f"jackett_{indexer_id}",
                "name": f"[Jackett] {indexer_name}",
                "domain": self._host,
                "encoding": "utf-8",
                "public": False,
                "search": {
                    "paths": [
                        {
                            "path": f"/api/v2.0/indexers/{indexer_id}/results/torznab/api",
                            "method": "get"
                        }
                    ],
                    "params": {
                        "apikey": self._api_key,
                        "t": "search",
                        "q": "{{ .Keywords }}",
                        "cat": "{{ .Categories }}"
                    }
                },
                "category": categories
            }
            
            return indexer_config
        except Exception as e:
            print(f"【{self.plugin_name}】格式化索引器异常: {str(e)}")
            return None

    def _add_jackett_indexers(self):
        """
        添加Jackett索引器到MoviePilot
        """
        try:
            # 获取Jackett索引器列表
            jackett_indexers = self._fetch_jackett_indexers()
            if not jackett_indexers:
                print(f"【{self.plugin_name}】未获取到Jackett索引器")
                return
            
            # 清理之前添加的索引器
            self._remove_added_indexers()
            
            added_count = 0
            for jackett_indexer in jackett_indexers:
                try:
                    indexer_id = jackett_indexer.get("id", "")
                    indexer_name = jackett_indexer.get("name", "")
                    
                    # 如果指定了索引器列表，则只添加指定的索引器
                    if self._indexers and indexer_id not in self._indexers:
                        continue
                    
                    # 格式化索引器配置
                    indexer_config = self._format_indexer(jackett_indexer)
                    if not indexer_config:
                        continue
                    
                    # 尝试通过站点助手添加索引器（新版本API）
                    try:
                        # 使用站点助手注册自定义站点
                        from app.helper.sites import SitesHelper
                        sites_helper = SitesHelper()
                        
                        # 构建站点配置
                        site_config = {
                            "id": indexer_config["id"],
                            "name": indexer_config["name"],
                            "domain": indexer_config["domain"],
                            "encoding": indexer_config["encoding"],
                            "public": indexer_config["public"],
                            "proxy": False,
                            "parser": "JACKETT",
                            "ua": "MoviePilot/2.0",
                            "search": indexer_config["search"]
                        }
                        
                        # 尝试添加站点
                        if hasattr(sites_helper, 'add_custom_site'):
                            sites_helper.add_custom_site(site_config)
                        elif hasattr(sites_helper, 'register_site'):
                            sites_helper.register_site(site_config)
                        
                        self._added_indexers.append(indexer_config["id"])
                        added_count += 1
                        print(f"【{self.plugin_name}】成功添加索引器: {indexer_name}")
                        
                    except Exception as api_error:
                        print(f"【{self.plugin_name}】通过API添加索引器失败: {str(api_error)}")
                        # 如果API方式失败，尝试直接保存配置
                        try:
                            self.save_data(f"indexer_{indexer_id}", indexer_config)
                            self._added_indexers.append(indexer_config["id"])
                            added_count += 1
                            print(f"【{self.plugin_name}】通过配置保存索引器: {indexer_name}")
                        except Exception as save_error:
                            print(f"【{self.plugin_name}】保存索引器配置失败: {str(save_error)}")
                        
                except Exception as e:
                    print(f"【{self.plugin_name}】添加索引器 {indexer_name} 异常: {str(e)}")
                    continue
            
            print(f"【{self.plugin_name}】共添加了 {added_count} 个Jackett索引器")
            
        except Exception as e:
            print(f"【{self.plugin_name}】添加Jackett索引器异常: {str(e)}")
            import traceback
            print(f"【{self.plugin_name}】异常详情: {traceback.format_exc()}")

    def _remove_added_indexers(self):
        """
        移除之前添加的索引器
        """
        try:
            if not self._added_indexers:
                return
            
            # 尝试通过站点助手移除
            try:
                from app.helper.sites import SitesHelper
                sites_helper = SitesHelper()
                
                for indexer_id in self._added_indexers:
                    try:
                        if hasattr(sites_helper, 'remove_custom_site'):
                            sites_helper.remove_custom_site(indexer_id)
                        elif hasattr(sites_helper, 'unregister_site'):
                            sites_helper.unregister_site(indexer_id)
                        print(f"【{self.plugin_name}】移除索引器: {indexer_id}")
                    except Exception as e:
                        print(f"【{self.plugin_name}】移除索引器 {indexer_id} 异常: {str(e)}")
                        # 如果API移除失败，尝试删除保存的配置
                        try:
                            self.del_data(f"indexer_{indexer_id.replace('jackett_', '')}")
                        except Exception:
                            pass
                            
            except ImportError:
                # 如果无法导入站点助手，清理保存的配置数据
                for indexer_id in self._added_indexers:
                    try:
                        self.del_data(f"indexer_{indexer_id.replace('jackett_', '')}")
                    except Exception:
                        pass
            
            self._added_indexers.clear()
            
        except Exception as e:
            print(f"【{self.plugin_name}】移除索引器异常: {str(e)}")

    def get_service(self) -> List[Dict[str, Any]]:
        """
        注册插件公共服务
        """
        services = []
        if self.get_state():
            services.append({
                "id": "jackett_sync",
                "name": "同步Jackett索引器",
                "trigger": "interval",
                "func": self._sync_indexers,
                "kwargs": {"hours": 6}  # 每6小时同步一次
            })
        return services

    def _sync_indexers(self):
        """
        定时同步Jackett索引器
        """
        try:
            if self._enabled and self._host and self._api_key:
                print(f"【{self.plugin_name}】开始定时同步索引器...")
                self._add_jackett_indexers()
                print(f"【{self.plugin_name}】定时同步完成")
        except Exception as e:
    def get_indexers(self) -> Dict[str, Any]:
        """
        API接口：获取Jackett索引器列表
        """
        try:
            indexers = self._fetch_jackett_indexers()
            indexer_list = []
            
            for indexer in indexers:
                indexer_list.append({
                    "id": indexer.get("id", ""),
                    "name": indexer.get("name", ""),
                    "description": indexer.get("description", ""),
                    "configured": indexer.get("configured", False)
                })
            
            return {
                "code": 0,
                "message": "success",
                "data": {
                    "indexers": indexer_list,
                    "total": len(indexer_list)
                }
            }
        except Exception as e:
            return {
                "code": 1,
                "message": f"获取索引器列表失败: {str(e)}",
                "data": None
            }

    def reload_indexers(self) -> Dict[str, Any]:
        """
        API接口：重新加载Jackett索引器
        """
        try:
            self._add_jackett_indexers()
            return {
                "code": 0,
                "message": "重新加载索引器成功",
                "data": None
            }
        except Exception as e:
            return {
                "code": 1,
                "message": f"重新加载索引器失败: {str(e)}",
                "data": None
            }

    def stop_service(self):
        """
        停止插件服务
        """
        try:
            print(f"【{self.plugin_name}】正在停止服务...")
            
            # 注销事件处理器（兼容处理）
            try:
                if hasattr(self, 'eventmanager') and self.eventmanager:
                    self.eventmanager.unregister("jackett.reload", self._handle_reload_command)
                    self.eventmanager.unregister("jackett.status", self._handle_status_command)
                elif eventmanager:
                    eventmanager.unregister("jackett.reload", self._handle_reload_command)
                    eventmanager.unregister("jackett.status", self._handle_status_command)
            except Exception as e:
                print(f"【{self.plugin_name}】注销事件处理器异常: {str(e)}")
            
            # 移除添加的索引器
            self._remove_added_indexers()
            
            print(f"【{self.plugin_name}】服务已停止")
        except Exception as e:
            print(f"【{self.plugin_name}】停止服务异常: {str(e)}")