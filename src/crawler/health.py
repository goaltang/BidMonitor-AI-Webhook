"""
网站健康检测模块

定期探测目标网站的可访问性，状态分级：
- ok    (🟢): HTTP 200 且响应 < 3s
- slow  (🟡): HTTP 200 但响应 3~10s
- down  (🔴): HTTP 非 200 或超时/异常
"""

import time
import threading
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

import requests


@dataclass
class HealthResult:
    status: str          # "ok" | "slow" | "down"
    status_code: int     # HTTP 状态码，异常时为 0
    response_time: float # 秒
    checked_at: str      # ISO 格式时间
    message: str         # 详细消息


class SiteHealthChecker:
    """网站健康状态检测器
    
    支持并发批量检测和结果缓存，避免频繁请求。
    """
    
    # 状态阈值（秒）
    SLOW_THRESHOLD = 3.0
    TIMEOUT = 10.0
    # 最小检测间隔（秒）
    MIN_CHECK_INTERVAL = 300  # 5 分钟
    
    def __init__(self):
        self._cache: Dict[str, HealthResult] = {}
        self._last_check: Dict[str, float] = {}
        self._lock = threading.Lock()
    
    def check_site(self, url: str, force: bool = False) -> HealthResult:
        """检测单个网站的健康状态
        
        Args:
            url: 目标网站 URL
            force: 是否强制检测（忽略缓存间隔）
            
        Returns:
            HealthResult 对象
        """
        now = time.time()
        
        with self._lock:
            last = self._last_check.get(url, 0)
            if not force and (now - last) < self.MIN_CHECK_INTERVAL:
                cached = self._cache.get(url)
                if cached:
                    return cached
        
        result = self._do_check(url)
        
        with self._lock:
            self._cache[url] = result
            self._last_check[url] = now
        
        return result
    
    def _do_check(self, url: str) -> HealthResult:
        """实际执行 HTTP 检测"""
        start = time.time()
        try:
            resp = requests.head(
                url,
                timeout=self.TIMEOUT,
                allow_redirects=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            elapsed = time.time() - start
            
            if resp.status_code == 200:
                if elapsed < self.SLOW_THRESHOLD:
                    status = "ok"
                    msg = f"响应正常 ({elapsed:.1f}s)"
                else:
                    status = "slow"
                    msg = f"响应较慢 ({elapsed:.1f}s)"
            else:
                status = "down"
                msg = f"HTTP {resp.status_code}"
            
            return HealthResult(
                status=status,
                status_code=resp.status_code,
                response_time=elapsed,
                checked_at=datetime.now().isoformat(),
                message=msg
            )
        except requests.exceptions.Timeout:
            return HealthResult(
                status="down",
                status_code=0,
                response_time=self.TIMEOUT,
                checked_at=datetime.now().isoformat(),
                message="请求超时"
            )
        except requests.exceptions.ConnectionError:
            return HealthResult(
                status="down",
                status_code=0,
                response_time=0,
                checked_at=datetime.now().isoformat(),
                message="连接失败"
            )
        except Exception as e:
            return HealthResult(
                status="down",
                status_code=0,
                response_time=0,
                checked_at=datetime.now().isoformat(),
                message=f"异常: {str(e)[:50]}"
            )
    
    def check_all_sites(self, sites: Dict[str, str],
                        callback: Optional[Callable[[str, HealthResult], None]] = None,
                        force: bool = False) -> Dict[str, HealthResult]:
        """批量检测多个网站（并发）
        
        Args:
            sites: {site_key: url}
            callback: 每个站点检测完成后的回调 (key, result)
            force: 是否强制检测
            
        Returns:
            {site_key: HealthResult}
        """
        results = {}
        
        def check_one(key: str, url: str):
            result = self.check_site(url, force=force)
            results[key] = result
            if callback:
                callback(key, result)
        
        threads = []
        for key, url in sites.items():
            t = threading.Thread(target=check_one, args=(key, url), daemon=True)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join(timeout=15)
        
        return results
    
    def get_status(self, url: str) -> Optional[HealthResult]:
        """获取缓存中的健康状态（不触发检测）"""
        return self._cache.get(url)
    
    def get_status_icon(self, url: str) -> str:
        """获取状态对应的图标字符"""
        result = self._cache.get(url)
        if not result:
            return "⚪"
        return {"ok": "🟢", "slow": "🟡", "down": "🔴"}.get(result.status, "⚪")
    
    def clear_cache(self):
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
            self._last_check.clear()
