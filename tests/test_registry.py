"""
测试爬虫注册表
"""
import pytest

from crawler.registry import (
    register_crawler,
    get_all_crawlers,
    get_crawler_class,
    CRAWLER_REGISTRY,
)
from crawler.base import BaseCrawler


class DummyCrawler(BaseCrawler):
    """测试用爬虫"""
    name = "dummy"
    base_url = "https://example.com"

    def get_list_urls(self):
        return [self.base_url]

    def parse(self, html):
        return []


class TestRegistry:
    """爬虫注册表测试"""

    def setup_method(self):
        """每个测试前清理注册表"""
        CRAWLER_REGISTRY.clear()

    def test_register_crawler(self):
        """装饰器注册成功"""
        decorator = register_crawler("test_dummy")
        decorated = decorator(DummyCrawler)
        assert decorated is DummyCrawler
        assert "test_dummy" in CRAWLER_REGISTRY
        assert CRAWLER_REGISTRY["test_dummy"] is DummyCrawler

    def test_register_non_baseclass_fails(self):
        """非 BaseCrawler 子类注册失败"""
        class NotACrawler:
            pass

        with pytest.raises(TypeError):
            register_crawler("bad")(NotACrawler)

    def test_get_all_crawlers(self):
        """获取所有爬虫"""
        register_crawler("a")(DummyCrawler)
        register_crawler("b")(DummyCrawler)
        crawlers = get_all_crawlers()
        assert len(crawlers) == 2
        assert "a" in crawlers
        assert "b" in crawlers

    def test_get_crawler_class(self):
        """按名称获取爬虫类"""
        register_crawler("dummy")(DummyCrawler)
        cls = get_crawler_class("dummy")
        assert cls is DummyCrawler

    def test_get_crawler_class_not_found(self):
        """获取未注册的爬虫抛出异常"""
        with pytest.raises(KeyError):
            get_crawler_class("nonexistent")

    def test_name_injection(self):
        """注册时注入 name 属性"""
        register_crawler("injected_name")(DummyCrawler)
        assert DummyCrawler.name == "injected_name"
