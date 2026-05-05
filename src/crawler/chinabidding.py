"""
中国采购与招标网爬虫 - 修复版2
网站：https://www.chinabidding.com.cn/
"""
from typing import List, Dict, Any
from urllib.parse import urljoin
from .base import BaseCrawler, BidInfo
from .registry import register_crawler


@register_crawler('chinabidding')
class ChinaBiddingCrawler(BaseCrawler):
    """中国采购与招标网爬虫"""
    
    name = "chinabidding"
    base_url = "https://www.chinabidding.com.cn"
    
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
        """使用正确的列表页URL"""
        return [
            # 综合要闻
            "https://www.chinabidding.com.cn/html/3000000009866/1.html",
            # 行业动态  
            "https://www.chinabidding.com.cn/html/3000000009966/1.html",
            # 首页
            "https://www.chinabidding.com.cn/",
        ]
    
    def parse(self, html: str) -> List[BidInfo]:
        """解析页面"""
        bids = []
        soup = self.parse_html(html)
        
        # 查找所有链接
        items = soup.find_all('a')
        
        for item in items:
            try:
                title = item.get_text(strip=True)
                if not title or len(title) < 10:
                    continue
                
                url = item.get('href', '')
                if not url or url.startswith('javascript'):
                    continue
                if not url.startswith('http'):
                    url = urljoin(self.base_url, url)
                
                bids.append(BidInfo(
                    title=title,
                    url=url,
                    publish_date="",
                    source="中国采购与招标网"
                ))
                
            except Exception as e:
                self.logger.warning(f"Parse error: {e}")
        
        return bids
