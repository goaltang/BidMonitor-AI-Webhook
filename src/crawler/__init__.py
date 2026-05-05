"""
爬虫模块

导入此包时自动注册所有内置爬虫。
"""

# 导入注册表
from .registry import register_crawler, get_all_crawlers, get_crawler_class

# 自动导入所有内置爬虫，触发装饰器注册
from .ccgp import CCGPCrawler
from .chinabidding import ChinaBiddingCrawler
from .ebnew import EbnewCrawler
from .plap import PLAPCrawler
from .bidcenter import BidcenterCrawler
from .chinatender import ChinaTenderCrawler
from .ggzy import GGZYCrawler
from .dlnyzb import DlnyzbCrawler
from .qianlima import QianlimaCrawler

__all__ = [
    'register_crawler',
    'get_all_crawlers',
    'get_crawler_class',
    'BaseCrawler',
    'BidInfo',
]
