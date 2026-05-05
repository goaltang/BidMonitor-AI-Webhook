"""
行业定义层 - 高低压成套设备

本模块集中管理所有与行业相关的定义和配置。
当需要适配其他行业时，主要修改此目录下的文件即可。
"""

from .industry import (
    INDUSTRY_NAME,
    INDUSTRY_VERSION,
    PRODUCT_KEYWORDS,
    PRODUCT_CATEGORIES,
    DEFAULT_INCLUDE_KEYWORDS,
    DEFAULT_EXCLUDE_KEYWORDS,
    DEFAULT_MUST_CONTAIN_KEYWORDS,
    DEFAULT_SEARCH_KEYWORDS,
)

from .sites import (
    get_default_sites,
    get_builtin_crawler_sites,
    get_sites,
    get_site_config,
    get_categories,
    get_sites_by_category,
    get_default_enabled_sites,
    get_all_site_keys,
    validate_enabled_sites,
    SITE_CATEGORIES,
    SITES,
)
from .prompts import get_ai_system_prompt

__all__ = [
    "INDUSTRY_NAME",
    "INDUSTRY_VERSION",
    "PRODUCT_KEYWORDS",
    "PRODUCT_CATEGORIES",
    "DEFAULT_INCLUDE_KEYWORDS",
    "DEFAULT_EXCLUDE_KEYWORDS",
    "DEFAULT_MUST_CONTAIN_KEYWORDS",
    "DEFAULT_SEARCH_KEYWORDS",
    "get_default_sites",
    "get_builtin_crawler_sites",
    "get_sites",
    "get_site_config",
    "get_categories",
    "get_sites_by_category",
    "get_default_enabled_sites",
    "get_all_site_keys",
    "validate_enabled_sites",
    "SITE_CATEGORIES",
    "SITES",
    "get_ai_system_prompt",
]
