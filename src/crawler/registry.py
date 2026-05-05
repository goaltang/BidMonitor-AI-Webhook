"""
爬虫注册表 - 装饰器自动注册

使用方式：
    from .registry import register_crawler
    
    @register_crawler('ccgp')
    class CCGPCrawler(BaseCrawler):
        ...
"""
from typing import Dict, Type

from .base import BaseCrawler

CRAWLER_REGISTRY: Dict[str, Type[BaseCrawler]] = {}


def register_crawler(name: str):
    """爬虫注册装饰器
    
    Args:
        name: 爬虫唯一标识名
        
    Usage:
        @register_crawler('ccgp')
        class CCGPCrawler(BaseCrawler):
            ...
    """
    def decorator(cls: Type[BaseCrawler]) -> Type[BaseCrawler]:
        if not issubclass(cls, BaseCrawler):
            raise TypeError(f"爬虫类必须继承 BaseCrawler: {cls.__name__}")
        CRAWLER_REGISTRY[name] = cls
        # 同时把 name 注入到类上（避免类属性与注册名不一致）
        cls.name = name
        return cls
    return decorator


def get_all_crawlers() -> Dict[str, Type[BaseCrawler]]:
    """获取所有已注册的爬虫类"""
    return CRAWLER_REGISTRY.copy()


def get_crawler_class(name: str) -> Type[BaseCrawler]:
    """根据名称获取爬虫类"""
    if name not in CRAWLER_REGISTRY:
        raise KeyError(f"未注册的爬虫: {name}，可用: {list(CRAWLER_REGISTRY.keys())}")
    return CRAWLER_REGISTRY[name]
