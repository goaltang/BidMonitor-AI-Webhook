"""
网站健康检测模块 V2 — 探测与爬取统一

核心变化：不再自己发裸 HTTP 请求，而是调用 Crawler.probe()。
探测通过 = 该站点可用真实爬取路径正常访问并解析到数据。

状态分级：
- ok        (🟢): 成功解析到数据，响应 < 3s
- slow      (🟡): 成功解析到数据，响应 3~10s
- degraded  (🟠): 请求成功但解析到0条数据（网站可能改版）
- down      (🔴): 请求失败或异常
"""

import time
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class HealthResult:
    status: str = "down"          # "ok" | "slow" | "degraded" | "down"
    status_code: int = 0          # HTTP 状态码（业务探测不关注，保留兼容）
    response_time: float = 0.0    # 秒
    checked_at: str = ""          # ISO 格式时间
    message: str = ""             # 详细消息
    sample: str = ""              # 探测时抓到的样本（如标题）
    error_type: str = ""          # 错误分类


class SiteHealthChecker:
    """网站健康状态检测器 V2
    
    探测逻辑下沉到各 Crawler 实现，确保"探测通过 = 能爬取"。
    支持将探测结果持久化到 Storage。
    """
    
    # 状态阈值（秒）
    SLOW_THRESHOLD = 3.0
    TIMEOUT = 30.0
    # 最小检测间隔（秒）
    MIN_CHECK_INTERVAL = 300  # 5 分钟
    
    def __init__(self, storage=None, alert_manager=None):
        self._cache: Dict[str, HealthResult] = {}
        self._last_check: Dict[str, float] = {}
        self._lock = threading.Lock()
        self.storage = storage  # Phase 2: 可选的持久化存储
        self.alert_manager = alert_manager  # Phase 3: 可选的告警管理器
    
    def _create_crawler(self, site_key: str, site_cfg: Dict[str, Any]) -> Optional[Any]:
        """根据站点配置创建对应的 Crawler 实例（仅用于探测）
        
        Args:
            site_key: 站点标识
            site_cfg: 站点配置字典（来自 domain.sites.SITES）
            
        Returns:
            Crawler 实例或 None
        """
        from .custom import CustomCrawler
        from .registry import get_all_crawlers
        
        crawler_type = site_cfg.get('crawler_type', 'custom')
        name = site_cfg.get('name', site_key)
        url = site_cfg.get('url', '')
        use_selenium = site_cfg.get('use_selenium', False)
        
        # 构建探测专用配置（轻量）
        timeout = site_cfg.get('timeout')
        probe_config = {
            'timeout': min(timeout, 30) if timeout is not None else 30,
            'max_retries': 1,  # 探测时减少重试，加快反馈
            'request_delay': 0,
        }
        
        try:
            # 1. 内置专用爬虫
            if crawler_type == 'builtin':
                crawler_classes = get_all_crawlers()
                if site_key in crawler_classes:
                    return crawler_classes[site_key](probe_config)
            
            # 2. 自定义 / 通用爬虫
            if not url:
                return None
            
            if use_selenium:
                from .selenium_crawler import SeleniumCrawler
                return SeleniumCrawler(probe_config, name, url, headless=True)
            else:
                return CustomCrawler(probe_config, name, url)
                
        except Exception:
            # 如果构建 crawler 失败，返回 None，上层会标记为 down
            return None
        
        return None
    
    def check_site(self, site_key: str, site_cfg: Dict[str, Any], force: bool = False) -> HealthResult:
        """检测单个网站的健康状态
        
        Args:
            site_key: 站点标识
            site_cfg: 站点配置字典
            force: 是否强制检测（忽略缓存间隔）
            
        Returns:
            HealthResult 对象
        """
        now = time.time()
        
        with self._lock:
            last = self._last_check.get(site_key, 0)
            if not force and (now - last) < self.MIN_CHECK_INTERVAL:
                cached = self._cache.get(site_key)
                if cached:
                    return cached
        
        crawler = self._create_crawler(site_key, site_cfg)
        if crawler is None:
            result = HealthResult(
                status="down",
                status_code=0,
                response_time=0.0,
                checked_at=datetime.now().isoformat(),
                message="无法创建爬虫实例",
                error_type="config"
            )
        else:
            try:
                probe = crawler.probe()
                elapsed = probe.get('latency', 0.0)
                
                status = probe.get('status', 'down')
                # 统一 slow 阈值
                if status == 'ok' and elapsed >= self.SLOW_THRESHOLD:
                    status = 'slow'
                
                # 生成友好消息
                if status == 'ok':
                    sample = probe.get('sample', '')
                    msg = f"探测成功 ({elapsed:.1f}s) 样本: {sample[:30]}..."
                elif status == 'slow':
                    msg = f"响应较慢 ({elapsed:.1f}s)"
                elif status == 'degraded':
                    msg = f"功能降级: {probe.get('error', '')}"
                else:
                    msg = f"探测失败: {probe.get('error', '')}"
                
                result = HealthResult(
                    status=status,
                    status_code=200 if status in ('ok', 'slow', 'degraded') else 0,
                    response_time=elapsed,
                    checked_at=datetime.now().isoformat(),
                    message=msg,
                    sample=probe.get('sample', ''),
                    error_type=probe.get('error_type', '')
                )
            except Exception as e:
                result = HealthResult(
                    status="down",
                    status_code=0,
                    response_time=0.0,
                    checked_at=datetime.now().isoformat(),
                    message=f"探测异常: {str(e)[:50]}",
                    error_type=type(e).__name__
                )
        
        with self._lock:
            self._cache[site_key] = result
            self._last_check[site_key] = now
        
        # Phase 2: 持久化探测记录
        if self.storage is not None:
            try:
                self.storage.save_probe_log(
                    site_key=site_key,
                    status=result.status,
                    latency_ms=int(result.response_time * 1000),
                    error_type=result.error_type,
                    sample=result.sample
                )
            except Exception:
                # 存储失败不应影响检测流程
                pass
        
        # Phase 3: 状态变更告警
        if self.alert_manager is not None:
            try:
                site_name = site_cfg.get('name') if isinstance(site_cfg, dict) else None
                self.alert_manager.check_and_notify(site_key, site_name)
            except Exception:
                # 告警失败不应影响检测流程
                pass
        
        return result
    
    def check_all_sites(self, sites: Dict[str, Dict[str, Any]],
                        callback: Optional[Callable[[str, HealthResult], None]] = None,
                        force: bool = False) -> Dict[str, HealthResult]:
        """批量检测多个网站（并发）
        
        Args:
            sites: {site_key: site_cfg}
            callback: 每个站点检测完成后的回调 (key, result)
            force: 是否强制检测
            
        Returns:
            {site_key: HealthResult}
        """
        results = {}
        
        def check_one(key: str, cfg: Dict[str, Any]):
            result = self.check_site(key, cfg, force=force)
            results[key] = result
            if callback:
                callback(key, result)
        
        threads = []
        for key, cfg in sites.items():
            t = threading.Thread(target=check_one, args=(key, cfg), daemon=True)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join(timeout=60)  # 探测可能慢，给足时间
        
        return results
    
    def get_status(self, site_key: str) -> Optional[HealthResult]:
        """获取缓存中的健康状态（不触发检测）"""
        return self._cache.get(site_key)
    
    def get_status_icon(self, site_key: str) -> str:
        """获取状态对应的图标字符"""
        result = self._cache.get(site_key)
        if not result:
            return "⚪"
        return {"ok": "🟢", "slow": "🟡", "degraded": "🟠", "down": "🔴"}.get(result.status, "⚪")
    
    def clear_cache(self):
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
            self._last_check.clear()
