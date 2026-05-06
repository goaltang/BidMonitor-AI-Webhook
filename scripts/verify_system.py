"""
系统验证脚本 - 验证重构后的核心流程
"""
import sys
import os

# 修复 Windows PowerShell 中文输出乱码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_config_loading():
    """验证配置加载"""
    print("[1/5] 测试配置加载...")
    from config.loader import load_config
    config = load_config('config/config.yaml')
    assert config.industry.include, "包含关键词不应为空"
    assert "高低压成套设备" in config.industry.include, "应包含行业核心词"
    print(f"  [OK] 配置加载成功，包含 {len(config.industry.include)} 个关键词")
    return config

def test_crawler_registry():
    """验证爬虫注册表"""
    print("[2/5] 测试爬虫注册表...")
    from crawler.registry import get_all_crawlers
    crawlers = get_all_crawlers()
    expected = {'ccgp', 'chinabidding', 'ebnew', 'plap'}
    missing = expected - set(crawlers.keys())
    assert not missing, f"爬虫注册表缺失: {missing}"
    print(f"  [OK] 爬虫注册表正常，共 {len(crawlers)} 个爬虫: {list(crawlers.keys())}")

def test_keyword_matcher():
    """验证关键词匹配器"""
    print("[3/5] 测试关键词匹配器...")
    from matcher.keyword import KeywordMatcher
    from domain.industry import DEFAULT_INCLUDE_KEYWORDS, DEFAULT_EXCLUDE_KEYWORDS
    matcher = KeywordMatcher(
        include_keywords=DEFAULT_INCLUDE_KEYWORDS,
        exclude_keywords=DEFAULT_EXCLUDE_KEYWORDS
    )
    # 应匹配
    result = matcher.match("某项目采购KYN28高压开关柜")
    assert result.matched, "应匹配包含行业关键词的标题"
    # 应排除
    result2 = matcher.match("某项目开关柜设计服务")
    assert not result2.matched, "应排除包含排除词的标题"
    assert result2.excluded_by == "设计"
    print("  [OK] 关键词匹配器工作正常")

def test_monitor_core_init():
    """验证监控核心初始化"""
    print("[4/5] 测试监控核心初始化...")
    from monitor_core import MonitorCore
    from domain.industry import DEFAULT_INCLUDE_KEYWORDS, DEFAULT_EXCLUDE_KEYWORDS
    core = MonitorCore(
        keywords=DEFAULT_INCLUDE_KEYWORDS,
        exclude_keywords=DEFAULT_EXCLUDE_KEYWORDS,
    )
    assert len(core.crawlers) > 0, "应至少初始化一个爬虫"
    print(f"  [OK] MonitorCore 初始化成功，加载了 {len(core.crawlers)} 个爬虫")
    return core

def test_crawler_parse():
    """验证爬虫解析能力"""
    print("[5/5] 测试爬虫解析能力...")
    from crawler.chinabidding import ChinaBiddingCrawler
    from domain.industry import DEFAULT_SEARCH_KEYWORDS
    
    crawler = ChinaBiddingCrawler({
        'search_keywords': DEFAULT_SEARCH_KEYWORDS[:3]
    })
    
    # 用一个简单的 HTML 测试解析逻辑
    test_html = '''
    <html><body>
    <a href="/bid/123">某项目采购高低压成套设备招标公告</a>
    <a href="/bid/124">某项目办公家具采购</a>
    <a href="javascript:void(0)">无效链接</a>
    </body></html>
    '''
    bids = crawler.parse(test_html)
    assert len(bids) >= 1, "应至少解析出1个有效链接"
    assert any("高低压成套设备" in b.title for b in bids), "应包含目标标题"
    print(f"  [OK] 爬虫解析正常，从测试HTML中提取了 {len(bids)} 条信息")

def main():
    print("=" * 50)
    print("BidMonitor 系统验证")
    print("=" * 50)
    print()
    
    try:
        config = test_config_loading()
        test_crawler_registry()
        test_keyword_matcher()
        core = test_monitor_core_init()
        test_crawler_parse()
        
        print()
        print("=" * 50)
        print("[PASS] 全部验证通过！系统运行正常。")
        print("=" * 50)
        print()
        print("提示：")
        print("- 如需启动监控，请配置 config/config.yaml 中的邮箱信息")
        print("- 运行方式: python run.py")
        print("- 服务端方式: python server/app.py")
        return 0
        
    except Exception as e:
        print()
        print("=" * 50)
        print(f"[FAIL] 验证失败: {e}")
        print("=" * 50)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
