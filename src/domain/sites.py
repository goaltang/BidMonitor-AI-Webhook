"""
网站定义 - 高低压成套设备行业招标信息源

本文件是网站源配置的单一事实来源（Single Source of Truth）。
所有网站定义集中在此管理，包括：
1. 分类信息
2. 基础属性（名称、URL、爬虫类型）
3. 默认独立配置（可覆盖全局）

GUI 和爬虫层均从此文件导入网站定义，禁止在 gui.py 中硬编码。
"""

from typing import Dict, List, Any, Optional


# =============================================================================
# 分类定义
# =============================================================================

SITE_CATEGORIES: Dict[str, str] = {
    "通用招标平台": "覆盖面广，优先级高",
    "电网公司": "配电侧核心客户",
    "电力行业平台": "行业垂直信息",
    "发电集团": "电厂配电设备需求",
    "工程总包": "项目含配电设备",
}


# =============================================================================
# 网站定义（单一事实来源）
# =============================================================================

SITES: Dict[str, Dict[str, Any]] = {
    # === 专用爬虫支持的网站 ===
    "ccgp": {
        "name": "中国政府采购网",
        "url": "http://www.ccgp.gov.cn",
        "category": "通用招标平台",
        "crawler_type": "builtin",
        "enabled_by_default": True,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "chinabidding": {
        "name": "中国采购与招标网",
        "url": "https://www.chinabidding.cn/",
        "category": "通用招标平台",
        "crawler_type": "builtin",
        "enabled_by_default": True,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "ebnew": {
        "name": "必联网（国义招标）",
        "url": "http://www.ebnew.com",
        "category": "通用招标平台",
        "crawler_type": "builtin",
        "enabled_by_default": True,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "plap": {
        "name": "军队采购网",
        "url": "http://www.plap.cn",
        "category": "通用招标平台",
        "crawler_type": "builtin",
        "enabled_by_default": True,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },

    # === 通用招标平台 ===
    "chinabiddingcc": {
        "name": "中国采购招标网",
        "url": "http://www.chinabidding.cc/",
        "category": "通用招标平台",
        "crawler_type": "custom",
        "enabled_by_default": True,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "chinazbcg": {
        "name": "中国招投标信息网",
        "url": "http://www.chinazbcg.com",
        "category": "通用招标平台",
        "crawler_type": "custom",
        "enabled_by_default": True,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "ebidding": {
        "name": "国义招标",
        "url": "http://www.ebidding.com/portal/",
        "category": "通用招标平台",
        "crawler_type": "custom",
        "enabled_by_default": False,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "zjycgzx": {
        "name": "浙江云采购中心",
        "url": "https://www.zjycgzx.com",
        "category": "通用招标平台",
        "crawler_type": "custom",
        "enabled_by_default": False,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },

    # === 电网公司 ===
    "sgcc": {
        "name": "国家电网电子商务平台",
        "url": "https://ecp.sgcc.com.cn/",
        "category": "电网公司",
        "crawler_type": "custom",
        "enabled_by_default": True,
        "timeout": 45,
        "max_retries": 5,
        "request_delay": None,
        "headers": None,
        "use_selenium": True,
    },
    "csg": {
        "name": "中国南方电网供应链服务平台",
        "url": "http://www.bidding.csg.cn/",
        "category": "电网公司",
        "crawler_type": "custom",
        "enabled_by_default": True,
        "timeout": 45,
        "max_retries": 5,
        "request_delay": None,
        "headers": None,
        "use_selenium": True,
    },
    "sgccetp": {
        "name": "国网电子商务平台电工交易专区",
        "url": "https://sgccetp.com.cn/",
        "category": "电网公司",
        "crawler_type": "custom",
        "enabled_by_default": False,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },

    # === 电力行业平台 ===
    "dlzb": {
        "name": "中国电力招标网",
        "url": "http://www.dlzb.com/",
        "category": "电力行业平台",
        "crawler_type": "custom",
        "enabled_by_default": True,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "cpeinet": {
        "name": "中国电力设备信息网",
        "url": "http://www.cpeinet.com.cn/",
        "category": "电力行业平台",
        "crawler_type": "custom",
        "enabled_by_default": True,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },

    # === 发电集团 ===
    "gdtzb": {
        "name": "国电投招标网",
        "url": "http://www.gdtzb.com",
        "category": "发电集团",
        "crawler_type": "custom",
        "enabled_by_default": True,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "chng": {
        "name": "华能集团电子商务平台",
        "url": "http://ec.chng.com.cn/ecmall/",
        "category": "发电集团",
        "crawler_type": "custom",
        "enabled_by_default": True,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "chdtp": {
        "name": "中国华电电子商务平台",
        "url": "http://www.chdtp.com/",
        "category": "发电集团",
        "crawler_type": "custom",
        "enabled_by_default": True,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "cdt": {
        "name": "中国大唐电子商务平台",
        "url": "http://www.cdt-ec.com/",
        "category": "发电集团",
        "crawler_type": "custom",
        "enabled_by_default": True,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "neep": {
        "name": "国家能源e购",
        "url": "https://www.neep.shop/",
        "category": "发电集团",
        "crawler_type": "custom",
        "enabled_by_default": True,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "ceic": {
        "name": "国家能源集团生态协作平台",
        "url": "https://cooperation.ceic.com/",
        "category": "发电集团",
        "crawler_type": "custom",
        "enabled_by_default": False,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "crpower": {
        "name": "华润电力",
        "url": "https://b2b.crpower.com.cn",
        "category": "发电集团",
        "crawler_type": "custom",
        "enabled_by_default": False,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "cgnpc": {
        "name": "中广核电子商务平台",
        "url": "https://ecp.cgnpc.com.cn",
        "category": "发电集团",
        "crawler_type": "custom",
        "enabled_by_default": True,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "dongfang": {
        "name": "东方电气",
        "url": "http://nsrm.dongfang.com/",
        "category": "发电集团",
        "crawler_type": "custom",
        "enabled_by_default": False,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "ctg": {
        "name": "中国三峡电子采购平台",
        "url": "https://eps.ctg.com.cn/",
        "category": "发电集团",
        "crawler_type": "custom",
        "enabled_by_default": False,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "sdicc": {
        "name": "国投集团电子采购平台",
        "url": "https://www.sdicc.com.cn/",
        "category": "发电集团",
        "crawler_type": "custom",
        "enabled_by_default": False,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "powerbeijing": {
        "name": "北京京能电子商务平台",
        "url": "http://www.powerbeijing-ec.com",
        "category": "发电集团",
        "crawler_type": "custom",
        "enabled_by_default": False,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "hghn": {
        "name": "华光环能数字化采购管理平台",
        "url": "https://hgcg.hghngroup.com/",
        "category": "发电集团",
        "crawler_type": "custom",
        "enabled_by_default": False,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "cecep": {
        "name": "中国节能环保电子采购平台",
        "url": "http://www.ebidding.cecep.cn/",
        "category": "发电集团",
        "crawler_type": "custom",
        "enabled_by_default": False,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "gdg": {
        "name": "广州发展集团电子采购平台",
        "url": "https://eps.gdg.com.cn/",
        "category": "发电集团",
        "crawler_type": "custom",
        "enabled_by_default": False,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },

    # === 工程总包 ===
    "powerchina": {
        "name": "中国电建采购电子商务平台",
        "url": "http://ec.powerchina.cn",
        "category": "工程总包",
        "crawler_type": "custom",
        "enabled_by_default": True,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "powerchina_bid": {
        "name": "中国电建采购招标数智化平台",
        "url": "https://bid.powerchina.cn/bidweb/",
        "category": "工程总包",
        "crawler_type": "custom",
        "enabled_by_default": True,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "powerchina_ec": {
        "name": "中国电建设备物资集中采购平台",
        "url": "https://ec.powerchina.cn/",
        "category": "工程总包",
        "crawler_type": "custom",
        "enabled_by_default": True,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "powerchina_scm": {
        "name": "中国电建供应链云服务平台",
        "url": "https://scm.powerchina.cn/",
        "category": "工程总包",
        "crawler_type": "custom",
        "enabled_by_default": True,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "ceec": {
        "name": "中国能建电子采购平台",
        "url": "https://ec.ceec.net.cn/",
        "category": "工程总包",
        "crawler_type": "custom",
        "enabled_by_default": True,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
    "crc": {
        "name": "华润集团守正电子招标采购平台",
        "url": "https://szecp.crc.com.cn/",
        "category": "工程总包",
        "crawler_type": "custom",
        "enabled_by_default": False,
        "timeout": None,
        "max_retries": None,
        "request_delay": None,
        "headers": None,
        "use_selenium": None,
    },
}


# =============================================================================
# 导出 API
# =============================================================================

def get_sites() -> Dict[str, Dict[str, Any]]:
    """获取所有网站定义"""
    return dict(SITES)


def get_site_config(key: str) -> Optional[Dict[str, Any]]:
    """获取单个网站的配置"""
    return SITES.get(key)


def get_categories() -> Dict[str, str]:
    """获取所有分类定义"""
    return dict(SITE_CATEGORIES)


def get_sites_by_category() -> Dict[str, List[Dict[str, Any]]]:
    """按分类分组返回网站列表
    
    Returns:
        {分类名: [{key, name, url, ...}, ...]}
    """
    result: Dict[str, List[Dict[str, Any]]] = {cat: [] for cat in SITE_CATEGORIES}
    for key, cfg in SITES.items():
        cat = cfg.get("category", "其他")
        if cat not in result:
            result[cat] = []
        item = dict(cfg)
        item["key"] = key
        result[cat].append(item)
    return result


def get_default_enabled_sites() -> List[str]:
    """获取默认启用的网站 key 列表"""
    return [k for k, v in SITES.items() if v.get("enabled_by_default", False)]


def get_all_site_keys() -> List[str]:
    """获取所有支持的网站 key 列表"""
    return list(SITES.keys())


def validate_enabled_sites(enabled_sites: List[str]) -> tuple[List[str], List[str]]:
    """校验并过滤无效的站点配置
    
    Returns:
        (有效列表, 无效列表)
    """
    all_keys = set(SITES.keys())
    valid = [k for k in enabled_sites if k in all_keys]
    invalid = [k for k in enabled_sites if k not in all_keys]
    return valid, invalid


# =============================================================================
# 向后兼容 API（逐步淘汰）
# =============================================================================

def get_builtin_crawler_sites() -> Dict[str, Dict[str, str]]:
    """获取有专用爬虫支持的网站（兼容旧接口）"""
    return {
        k: {"name": v["name"], "url": v["url"]}
        for k, v in SITES.items()
        if v.get("crawler_type") == "builtin"
    }


def get_default_sites() -> Dict[str, Dict[str, str]]:
    """获取默认的内置网站列表（兼容旧接口）"""
    return {
        k: {"name": v["name"], "url": v["url"]}
        for k, v in SITES.items()
        if v.get("crawler_type") != "builtin"
    }
