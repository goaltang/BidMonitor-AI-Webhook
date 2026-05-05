"""
自定义通用爬虫 - 支持规则引擎（CSS选择器 + 翻页）
"""
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
from datetime import datetime
import re
from .base import BaseCrawler, BidInfo


class CustomCrawler(BaseCrawler):
    """自定义通用爬虫
    
    支持通过配置规则精确提取招标信息：
    - CSS 选择器定位列表项和字段
    - 翻页模式（单页/参数翻页）
    - 编码指定
    
    如果未配置规则，回退到旧行为（提取所有 <a> 链接）。
    """
    
    def __init__(self, config: dict, name: str, url: str, rules: Optional[Dict[str, Any]] = None):
        self._name = name
        self.url = url
        self.rules = rules or {}
        super().__init__(config)
        
    @property
    def name(self) -> str:
        return self._name
        
    def get_list_urls(self) -> List[str]:
        """生成列表页 URL（支持翻页）"""
        max_pages = self.rules.get('max_pages', 1)
        pattern = self.rules.get('pagination_pattern', '')
        
        if max_pages <= 1 or not pattern or '{page}' not in pattern:
            return [self.url]
        
        urls = []
        for page in range(1, max_pages + 1):
            urls.append(pattern.replace('{page}', str(page)))
        return urls
        
    def parse(self, html: str) -> List[BidInfo]:
        """解析 HTML 提取招标信息
        
        如果配置了 rules，使用 CSS 选择器精确提取。
        否则回退到旧行为（提取所有 <a> 链接）。
        """
        if self.rules and self.rules.get('list_selector'):
            return self._parse_with_rules(html)
        return self._parse_fallback(html)
    
    def _parse_with_rules(self, html: str) -> List[BidInfo]:
        """使用 CSS 选择器规则解析"""
        soup = self.parse_html(html)
        bids = []
        today = datetime.now().strftime('%Y-%m-%d')
        seen_urls = set()
        
        list_selector = self.rules.get('list_selector', '')
        title_selector = self.rules.get('title_selector', '')
        url_selector = self.rules.get('url_selector', 'a')
        date_selector = self.rules.get('date_selector', '')
        
        items = soup.select(list_selector)
        for item in items:
            # 提取标题
            title = ''
            if title_selector:
                title_el = item.select_one(title_selector)
                if title_el:
                    title = title_el.get_text(strip=True)
            else:
                title = item.get_text(strip=True)
            
            if not title or len(title) < 4:
                continue
            
            # 提取链接
            url = ''
            url_el = item.select_one(url_selector) if url_selector else item
            if url_el:
                if url_el.name == 'a':
                    url = url_el.get('href', '')
                else:
                    a_el = url_el.find('a')
                    if a_el:
                        url = a_el.get('href', '')
            
            if not url:
                continue
            if url.lower().startswith(('javascript:', '#', 'mailto:', 'tel:')):
                continue
            
            full_url = urljoin(self.url, url)
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)
            
            # 提取日期
            publish_date = today
            if date_selector:
                date_el = item.select_one(date_selector)
                if date_el:
                    raw_date = date_el.get_text(strip=True)
                    parsed = self._parse_date(raw_date)
                    if parsed:
                        publish_date = parsed
            
            bids.append(BidInfo(
                title=title,
                url=full_url,
                publish_date=publish_date,
                source=self.name
            ))
        
        return bids
    
    def _parse_fallback(self, html: str) -> List[BidInfo]:
        """旧行为回退：提取所有 <a> 链接"""
        soup = self.parse_html(html)
        bids = []
        today = datetime.now().strftime('%Y-%m-%d')
        seen_urls = set()
        
        for a in soup.find_all('a', href=True):
            text = a.get_text(strip=True)
            href = a['href']
            
            if not text or len(text) < 4:
                continue
            if href.lower().startswith(('javascript:', '#', 'mailto:', 'tel:')):
                continue
            
            full_url = urljoin(self.url, href)
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)
            
            bids.append(BidInfo(
                title=text,
                url=full_url,
                publish_date=today,
                source=self.name
            ))
        
        return bids
    
    def _parse_date(self, raw: str) -> Optional[str]:
        """尝试从字符串解析日期"""
        # 匹配常见中文日期格式：2024-01-15, 2024/01/15, 2024年01月15日
        patterns = [
            r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})',
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
        ]
        for pat in patterns:
            m = re.search(pat, raw)
            if m:
                y, mth, d = m.groups()
                return f"{y}-{int(mth):02d}-{int(d):02d}"
        return None
