"""
熔断器模块 — 基于探测历史的自动故障隔离

核心设计：
- 无内存状态，完全基于数据库历史记录决策，重启后自动恢复。
- 调度器在爬取前调用 should_skip()，爬取后调用 record()。
- 与 SiteHealthChecker 共用 site_probe_log 表，调度记录 error_type 标记为 'circuit'。
"""

from datetime import datetime, timedelta
from typing import Optional


class CircuitBreaker:
    """简单熔断器
    
    规则：
    - 最近 failure_threshold 次记录全部失败 → OPEN（跳过调度）
    - OPEN 后经过 cooldown_seconds → 允许一次 HALF_OPEN（试爬）
    - 试爬成功 → CLOSED（恢复正常）
    """
    
    def __init__(self, storage,
                 failure_threshold: int = 3,
                 recovery_threshold: int = 1,
                 cooldown_seconds: int = 300):
        """
        Args:
            storage: Storage 实例（用于读写 probe 历史）
            failure_threshold: 连续失败多少次后熔断
            recovery_threshold: 连续成功多少次后恢复
            cooldown_seconds: 熔断后多久允许试爬（秒）
        """
        self.storage = storage
        self.failure_threshold = max(1, failure_threshold)
        self.recovery_threshold = max(1, recovery_threshold)
        self.cooldown_seconds = cooldown_seconds
    
    def should_skip(self, site_key: str) -> bool:
        """判断该站点是否应该跳过本次调度
        
        Returns:
            True  → 熔断器开启，跳过该站点
            False → 允许爬取
        """
        history = self.storage.get_probe_history(site_key, limit=self.failure_threshold)
        
        # 记录不足阈值，不熔断（给新站点足够的机会）
        if len(history) < self.failure_threshold:
            return False
        
        # 最近 N 次是否全部失败？
        # 注意：degraded（能访问但解析不到数据）也算失败，因为它无法完成业务目标
        all_failed = all(h['status'] in ('down', 'degraded') for h in history)
        if not all_failed:
            return False
        
        # 最近 N 次全部失败，检查 cooldown
        # history 按时间倒序，[-1] 是最旧的一次
        oldest_time = datetime.fromisoformat(history[-1]['checked_at'])
        if datetime.now() - oldest_time > timedelta(seconds=self.cooldown_seconds):
            # cooldown 已过，允许一次试爬（HALF_OPEN）
            return False
        
        # 仍在 cooldown 窗口内，保持 OPEN
        return True
    
    def record(self, site_key: str, success: bool, latency_ms: int = 0):
        """记录一次调度层的爬取结果
        
        Args:
            site_key: 站点标识
            success: 是否成功爬到并解析到数据
            latency_ms: 耗时（毫秒），可选
        """
        status = 'ok' if success else 'down'
        self.storage.save_probe_log(
            site_key=site_key,
            status=status,
            latency_ms=latency_ms,
            error_type='circuit',
            sample=''
        )
    
    def get_state(self, site_key: str) -> str:
        """获取熔断器当前状态（用于日志/展示）
        
        Returns:
            "CLOSED" | "OPEN" | "HALF_OPEN"
        """
        history = self.storage.get_probe_history(site_key, limit=self.failure_threshold)
        
        if len(history) < self.failure_threshold:
            return "CLOSED"
        
        all_failed = all(h['status'] in ('down', 'degraded') for h in history)
        if not all_failed:
            return "CLOSED"
        
        oldest_time = datetime.fromisoformat(history[-1]['checked_at'])
        if datetime.now() - oldest_time > timedelta(seconds=self.cooldown_seconds):
            return "HALF_OPEN"
        
        return "OPEN"
    
    def get_site_summary(self, site_key: str) -> dict:
        """获取站点的熔断摘要（用于 GUI 展示）
        
        Returns:
            {
                "state": str,
                "success_rate_24h": float,
                "recent_failures": int,
            }
        """
        state = self.get_state(site_key)
        success_rate = self.storage.get_site_success_rate(site_key, window_hours=24)
        
        # 最近连续失败次数
        history = self.storage.get_probe_history(site_key, limit=20)
        recent_failures = 0
        for h in history:
            if h['status'] in ('down', 'degraded'):
                recent_failures += 1
            else:
                break
        
        return {
            "state": state,
            "success_rate_24h": success_rate,
            "recent_failures": recent_failures,
        }
