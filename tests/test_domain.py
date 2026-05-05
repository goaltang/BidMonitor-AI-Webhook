"""
测试行业定义层
"""
import pytest

from domain.industry import (
    INDUSTRY_NAME,
    PRODUCT_KEYWORDS,
    PRODUCT_CATEGORIES,
    DEFAULT_INCLUDE_KEYWORDS,
    DEFAULT_EXCLUDE_KEYWORDS,
    DEFAULT_SEARCH_KEYWORDS,
)
from domain.sites import get_default_sites, get_builtin_crawler_sites, validate_enabled_sites
from domain.prompts import get_ai_system_prompt


class TestIndustry:
    """行业定义测试"""

    def test_industry_name(self):
        """行业名称正确"""
        assert INDUSTRY_NAME == "高低压成套设备"

    def test_product_keywords_not_empty(self):
        """产品词库不为空"""
        assert len(PRODUCT_KEYWORDS) > 0
        assert "高低压成套设备" in PRODUCT_KEYWORDS
        assert "KYN28" in PRODUCT_KEYWORDS
        assert "GGD" in PRODUCT_KEYWORDS

    def test_product_categories(self):
        """产品分类结构正确"""
        assert "高压开关柜" in PRODUCT_CATEGORIES
        assert "低压配电柜" in PRODUCT_CATEGORIES
        assert "KYN28" in PRODUCT_CATEGORIES["高压开关柜"]
        assert "GGD" in PRODUCT_CATEGORIES["低压配电柜"]

    def test_default_keywords(self):
        """默认关键词包含核心词汇"""
        assert "高低压成套设备" in DEFAULT_INCLUDE_KEYWORDS
        assert "开关柜" in DEFAULT_INCLUDE_KEYWORDS
        assert "设计" in DEFAULT_EXCLUDE_KEYWORDS

    def test_default_search_keywords(self):
        """默认搜索关键词不为空"""
        assert len(DEFAULT_SEARCH_KEYWORDS) >= 3


class TestSites:
    """网站定义测试"""

    def test_default_sites_not_empty(self):
        """默认网站列表不为空"""
        sites = get_default_sites()
        assert len(sites) > 0
        assert "sgcc" in sites  # 国家电网
        assert "chinabidding" in sites

    def test_builtin_crawlers(self):
        """内置爬虫列表正确"""
        builtin = get_builtin_crawler_sites()
        assert "ccgp" in builtin
        assert "chinabidding" in builtin
        assert "ebnew" in builtin
        assert "plap" in builtin

    def test_validate_enabled_sites(self):
        """站点校验功能"""
        valid, invalid = validate_enabled_sites(["ccgp", "sgcc", "nonexistent_site"])
        assert "ccgp" in valid
        assert "sgcc" in valid
        assert "nonexistent_site" in invalid

    def test_site_has_required_fields(self):
        """每个站点都有名称和URL"""
        sites = get_default_sites()
        for key, info in sites.items():
            assert "name" in info, f"站点 {key} 缺少 name"
            assert "url" in info, f"站点 {key} 缺少 url"
            assert info["url"].startswith("http"), f"站点 {key} URL 格式错误"


class TestPrompts:
    """AI Prompt 测试"""

    def test_default_prompt_contains_industry(self):
        """默认提示词包含行业信息"""
        prompt = get_ai_system_prompt()
        assert "高低压成套设备" in prompt
        assert "KYN28" in prompt
        assert "GGD" in prompt

    def test_default_prompt_contains_conditions(self):
        """默认提示词包含判断条件"""
        prompt = get_ai_system_prompt()
        assert "符合条件" in prompt
        assert "排除条件" in prompt
        assert "relevant" in prompt

    def test_custom_prompt_override(self):
        """自定义提示词可覆盖默认值"""
        custom = "这是自定义提示词"
        prompt = get_ai_system_prompt(custom_prompt=custom)
        assert prompt == custom
