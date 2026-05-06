"""
军队采购网爬虫
网站：http://www.plap.mil.cn/
注意：军队采购网可能需要特殊处理
"""
from typing import List, Dict, Any
from urllib.parse import urljoin
from .base import BaseCrawler, BidInfo
from .registry import register_crawler


@register_crawler('plap')
class PLAPCrawler(BaseCrawler):
    """军队采购网爬虫"""
    
    name = "plap"
    base_url = "http://www.plap.mil.cn"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            from domain.industry import DEFAULT_SEARCH_KEYWORDS
        except ImportError:
            import sys, os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from domain.industry import DEFAULT_SEARCH_KEYWORDS
        self.search_keywords = config.get('search_keywords', DEFAULT_SEARCH_KEYWORDS[:3])
    
    def get_list_urls(self) -> List[str]:
        """生成URL列表"""
        # 军队采购网的公告页面
        return [
            "http://www.plap.mil.cn/xqgg/index.html",  # 需求公示
            "http://www.plap.mil.cn/zbgg/index.html",  # 招标公告
        ]
    
    def parse(self, html: str) -> List[BidInfo]:
        """解析公告列表页面"""
        bids = []
        soup = self.parse_html(html)
        
        # 查找所有结果项
        items = soup.select('ul.list li, div.list-item, table tr')
        
        for item in items:
            try:
                # 查找标题链接
                title_elem = item.select_one('a')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                if not title or len(title) < 5:
                    continue
                
                # 搜索词过滤已下沉到 KeywordMatcher 统一处理
                # 此处不再做标题硬过滤，避免标题不含搜索词但正文相关的招标被提前丢弃
                
                url = title_elem.get('href', '')
                if url and not url.startswith('http'):
                    url = urljoin(self.base_url, url)
                
                # 查找日期
                date_elem = item.select_one('span.date, td:last-child')
                publish_date = date_elem.get_text(strip=True) if date_elem else ""
                
                bids.append(BidInfo(
                    title=title,
                    url=url,
                    publish_date=publish_date,
                    source="军队采购网"
                ))
                
            except Exception as e:
                self.logger.warning(f"解析条目失败: {e}")
                continue
        
        return bids
