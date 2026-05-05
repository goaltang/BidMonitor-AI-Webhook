"""
网站定义 - 高低压成套设备行业招标信息源

本文件集中管理所有监控目标网站。
分为两类：
1. 内置专用爬虫支持的网站（有独立爬虫类）
2. 通用爬虫支持的网站（通过 CustomCrawler / SeleniumCrawler 抓取）
"""

from typing import Dict, List


# =============================================================================
# 内置爬虫支持的网站（需要对应爬虫类）
# =============================================================================

def get_builtin_crawler_sites() -> Dict[str, Dict[str, str]]:
    """获取有专用爬虫支持的网站"""
    return {
        'ccgp': {'name': '中国政府采购网', 'url': 'http://www.ccgp.gov.cn'},
        'chinabidding': {'name': '中国采购与招标网', 'url': 'https://www.chinabidding.com.cn'},
        'ebnew': {'name': '必联网（国义招标）', 'url': 'http://www.ebnew.com'},
        'plap': {'name': '军队采购网', 'url': 'http://www.plap.cn'},
    }


# =============================================================================
# 通用爬虫支持的网站（通过 CustomCrawler / SeleniumCrawler 抓取）
# =============================================================================

def get_default_sites() -> Dict[str, Dict[str, str]]:
    """获取默认的内置网站列表（适配高低压成套设备行业）
    
    分类说明：
    - 通用招标平台：覆盖面广，优先级高
    - 电网公司：配电侧核心客户
    - 电力行业平台：行业垂直信息
    - 发电集团：电厂配电设备需求
    - 工程总包：项目含配电设备
    """
    return {
        # === 通用招标平台（核心） ===
        'chinabidding': {'name': '中国采购与招标网', 'url': 'http://www.chinabidding.cn/'},
        'chinabiddingcc': {'name': '中国采购招标网', 'url': 'http://www.chinabidding.cc/'},
        'chinazbcg': {'name': '中国招投标信息网', 'url': 'http://www.chinazbcg.com'},
        'ebidding': {'name': '国义招标', 'url': 'http://www.ebidding.com/portal/'},
        'zjycgzx': {'name': '浙江云采购中心', 'url': 'https://www.zjycgzx.com'},
        # === 电网公司（配电侧核心客户） ===
        'sgcc': {'name': '国家电网电子商务平台', 'url': 'https://ecp.sgcc.com.cn/'},
        'csg': {'name': '中国南方电网供应链服务平台', 'url': 'http://www.bidding.csg.cn/'},
        'sgccetp': {'name': '国网电子商务平台电工交易专区', 'url': 'https://sgccetp.com.cn/'},
        # === 电力行业通用平台 ===
        'dlzb': {'name': '中国电力招标网', 'url': 'http://www.dlzb.com/'},
        'cpeinet': {'name': '中国电力设备信息网', 'url': 'http://www.cpeinet.com.cn/'},
        # === 发电集团（电厂配电设备需求） ===
        'gdtzb': {'name': '国电投招标网', 'url': 'http://www.gdtzb.com'},
        'chng': {'name': '华能集团电子商务平台', 'url': 'http://ec.chng.com.cn/ecmall/'},
        'chdtp': {'name': '中国华电电子商务平台', 'url': 'http://www.chdtp.com/'},
        'cdt': {'name': '中国大唐电子商务平台', 'url': 'http://www.cdt-ec.com/'},
        'neep': {'name': '国家能源e购', 'url': 'https://www.neep.shop/'},
        'ceic': {'name': '国家能源集团生态协作平台', 'url': 'https://cooperation.ceic.com/'},
        'crpower': {'name': '华润电力', 'url': 'https://b2b.crpower.com.cn'},
        'cgnpc': {'name': '中广核电子商务平台', 'url': 'https://ecp.cgnpc.com.cn'},
        'dongfang': {'name': '东方电气', 'url': 'http://nsrm.dongfang.com/'},
        'ctg': {'name': '中国三峡电子采购平台', 'url': 'https://eps.ctg.com.cn/'},
        'sdicc': {'name': '国投集团电子采购平台', 'url': 'https://www.sdicc.com.cn/'},
        'powerbeijing': {'name': '北京京能电子商务平台', 'url': 'http://www.powerbeijing-ec.com'},
        'hghn': {'name': '华光环能数字化采购管理平台', 'url': 'https://hgcg.hghngroup.com/'},
        'cecep': {'name': '中国节能环保电子采购平台', 'url': 'http://www.ebidding.cecep.cn/'},
        'gdg': {'name': '广州发展集团电子采购平台', 'url': 'https://eps.gdg.com.cn/'},
        # === 工程总包（项目含配电设备） ===
        'powerchina': {'name': '中国电建采购电子商务平台', 'url': 'http://ec.powerchina.cn'},
        'powerchina_bid': {'name': '中国电建采购招标数智化平台', 'url': 'https://bid.powerchina.cn/bidweb/'},
        'powerchina_ec': {'name': '中国电建设备物资集中采购平台', 'url': 'https://ec.powerchina.cn/'},
        'powerchina_scm': {'name': '中国电建供应链云服务平台', 'url': 'https://scm.powerchina.cn/'},
        'ceec': {'name': '中国能建电子采购平台', 'url': 'https://ec.ceec.net.cn/'},
        'crc': {'name': '华润集团守正电子招标采购平台', 'url': 'https://szecp.crc.com.cn/'},
    }


def get_all_site_keys() -> List[str]:
    """获取所有支持的网站 key 列表"""
    builtin = list(get_builtin_crawler_sites().keys())
    general = list(get_default_sites().keys())
    # 去重（chinabidding 等可能同时出现在两类中）
    seen = set()
    result = []
    for key in builtin + general:
        if key not in seen:
            seen.add(key)
            result.append(key)
    return result


def validate_enabled_sites(enabled_sites: List[str]) -> List[str]:
    """校验并过滤无效的站点配置
    
    Args:
        enabled_sites: 用户配置的启用站点列表
        
    Returns:
        过滤掉未定义站点后的有效列表
    """
    all_keys = set(get_all_site_keys())
    valid = [k for k in enabled_sites if k in all_keys]
    invalid = [k for k in enabled_sites if k not in all_keys]
    return valid, invalid
