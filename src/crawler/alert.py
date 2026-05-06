"""
站点告警通知模块 — 微信推送

当站点探测状态发生变更时（如正常->失败、失败->恢复），自动发送微信通知。
支持 PushPlus 和企业微信 Webhook。

特性：
- 基于数据库历史记录检测状态变更
- 同状态冷却机制（默认10分钟），避免消息轰炸
- 状态变更不受冷却限制，立即通知
"""

import time
import logging
from typing import Dict, Tuple, Optional


class SiteAlertManager:
    """站点告警管理器"""
    
    def __init__(self, storage, wechat_config: Optional[dict] = None, cooldown_seconds: int = 600):
        """
        Args:
            storage: Storage 实例（读取探测历史）
            wechat_config: 微信配置 {
                'provider': 'pushplus' | 'enterprise',
                'token': str,
                'webhook_url': str
            }
            cooldown_seconds: 同一站点同状态的最小告警间隔（秒）
        """
        self.storage = storage
        self.cooldown = cooldown_seconds
        self.logger = logging.getLogger("alert")
        self._last_alert: Dict[str, Tuple[str, float]] = {}  # site_key -> (status, timestamp)
        
        # 初始化微信通知器
        self._notifier = None
        self._provider = None
        if wechat_config:
            provider = wechat_config.get('provider', 'pushplus')
            try:
                if provider == 'pushplus' and wechat_config.get('token'):
                    from notifier.wechat import PushPlusNotifier
                    self._notifier = PushPlusNotifier(wechat_config['token'])
                    self._provider = 'pushplus'
                    self.logger.info("[Alert] PushPlus 告警通道已启用")
                elif provider == 'enterprise' and wechat_config.get('webhook_url'):
                    from notifier.wechat import EnterpriseWeChatNotifier
                    self._notifier = EnterpriseWeChatNotifier(wechat_config['webhook_url'])
                    self._provider = 'enterprise'
                    self.logger.info("[Alert] 企业微信告警通道已启用")
            except Exception as e:
                self.logger.error(f"[Alert] 微信通知器初始化失败: {e}")
    
    def check_and_notify(self, site_key: str, site_name: Optional[str] = None):
        """检测状态变更并发送通知
        
        Args:
            site_key: 站点标识（写入 site_probe_log 的 key）
            site_name: 站点显示名称（可选，默认从 domain.sites 查找）
        """
        if self._notifier is None:
            return
        
        # 获取最近 2 次探测记录
        history = self.storage.get_probe_history(site_key, limit=2)
        if len(history) < 2:
            return  # 记录不足，无法判断变更
        
        current_status = history[0]['status']
        previous_status = history[1]['status']
        
        if current_status == previous_status:
            return  # 无状态变更
        
        # 冷却检查：同一状态 N 分钟内不重复告警
        now = time.time()
        last = self._last_alert.get(site_key)
        if last and last[0] == current_status and (now - last[1]) < self.cooldown:
            self.logger.debug(f"[Alert] {site_key} 处于冷却期，跳过 {current_status} 告警")
            return
        
        # 发送通知
        display_name = self._resolve_display_name(site_key, site_name)
        self._send(display_name, site_key, current_status, previous_status)
        self._last_alert[site_key] = (current_status, now)
    
    def _resolve_display_name(self, site_key: str, site_name: Optional[str]) -> str:
        """解析站点显示名称"""
        if site_name:
            return site_name
        try:
            from domain.sites import get_sites
            sites = get_sites()
            if site_key in sites:
                return sites[site_key].get('name', site_key)
        except Exception:
            pass
        return site_key
    
    def _send(self, display_name: str, site_key: str, current: str, previous: str):
        """构建并发送告警消息"""
        # 获取统计信息
        success_rate = self.storage.get_site_success_rate(site_key, window_hours=24)
        latest = self.storage.get_latest_probe(site_key)
        checked_at = latest.get('checked_at', '')[:19] if latest else ''
        error_type = latest.get('error_type', '') if latest else ''
        
        # 状态图标映射
        status_icons = {
            'ok': '🟢',
            'slow': '🟡',
            'degraded': '🟠',
            'down': '🔴'
        }
        current_icon = status_icons.get(current, '⚪')
        previous_icon = status_icons.get(previous, '⚪')
        
        # 判断是告警还是恢复
        is_recovery = current in ('ok', 'slow') and previous in ('down', 'degraded')
        
        if self._provider == 'pushplus':
            self._send_pushplus(display_name, site_key, current, previous,
                                current_icon, previous_icon, is_recovery,
                                success_rate, checked_at, error_type)
        else:
            self._send_enterprise(display_name, site_key, current, previous,
                                  current_icon, previous_icon, is_recovery,
                                  success_rate, checked_at, error_type)
    
    def _send_pushplus(self, display_name, site_key, current, previous,
                       current_icon, previous_icon, is_recovery,
                       success_rate, checked_at, error_type):
        """PushPlus 推送"""
        if is_recovery:
            title = f"✅ 站点恢复 — {display_name}"
            header = f"<h3>✅ 站点恢复</h3>"
        else:
            title = f"⚠️ 站点告警 — {display_name}"
            header = f"<h3>⚠️ 站点告警</h3>"
        
        content_lines = [
            header,
            f"<p><b>{display_name}</b> 状态变更</p>",
            "<ul>",
            f"<li>当前状态: {current_icon} {self._status_label(current)}</li>",
            f"<li>之前状态: {previous_icon} {self._status_label(previous)}</li>",
            f"<li>24h可用率: {success_rate*100:.0f}%</li>",
        ]
        if checked_at:
            content_lines.append(f"<li>最近探测: {checked_at}</li>")
        if error_type:
            content_lines.append(f"<li>错误类型: {error_type}</li>")
        content_lines.append("</ul>")
        
        if not is_recovery:
            content_lines.append("<p><font color='gray'>建议: 检查网站是否改版或网络连接</font></p>")
        
        content = "\n".join(content_lines)
        
        try:
            result = self._notifier.send(title, content, template="html")
            if result:
                self.logger.info(f"[Alert] 微信告警已发送: {display_name} {previous}->{current}")
            else:
                self.logger.warning(f"[Alert] 微信告警发送失败: {display_name}")
        except Exception as e:
            self.logger.error(f"[Alert] 发送异常: {e}")
    
    def _send_enterprise(self, display_name, site_key, current, previous,
                         current_icon, previous_icon, is_recovery,
                         success_rate, checked_at, error_type):
        """企业微信 Markdown 推送"""
        if is_recovery:
            title = f"✅ 站点恢复 — {display_name}"
        else:
            title = f"⚠️ 站点告警 — {display_name}"
        
        lines = [
            f"## {title}",
            "",
            f"**{display_name}** 状态变更",
            "",
            f"- 当前状态: {current_icon} {self._status_label(current)}",
            f"- 之前状态: {previous_icon} {self._status_label(previous)}",
            f"- 24h可用率: {success_rate*100:.0f}%",
        ]
        if checked_at:
            lines.append(f"- 最近探测: {checked_at}")
        if error_type:
            lines.append(f"- 错误类型: {error_type}")
        
        if not is_recovery:
            lines.append("")
            lines.append("> 💡 建议: 检查网站是否改版或网络连接")
        
        content = "\n".join(lines)
        
        try:
            result = self._notifier.send_markdown(content)
            if result:
                self.logger.info(f"[Alert] 企业微信告警已发送: {display_name} {previous}->{current}")
            else:
                self.logger.warning(f"[Alert] 企业微信告警发送失败: {display_name}")
        except Exception as e:
            self.logger.error(f"[Alert] 发送异常: {e}")
    
    @staticmethod
    def _status_label(status: str) -> str:
        labels = {
            'ok': '访问正常',
            'slow': '响应较慢',
            'degraded': '功能降级',
            'down': '访问失败'
        }
        return labels.get(status, status)
