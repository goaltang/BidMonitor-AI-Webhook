import json
import logging

try:
    from .domain.prompts import get_ai_system_prompt
except ImportError:
    from domain.prompts import get_ai_system_prompt

try:
    from .ai_providers import (
        AIProvider,
        build_request_payload,
        parse_response,
        find_active_provider,
    )
except ImportError:
    from ai_providers import (
        AIProvider,
        build_request_payload,
        parse_response,
        find_active_provider,
    )


class AIGuard:
    def __init__(self, config=None, log_callback=None):
        self.logger = logging.getLogger("AIGuard")
        self.log_callback = log_callback  # GUI日志回调
        self.update_config(config)

    def log(self, message):
        """输出日志到GUI和logger"""
        if self.log_callback:
            self.log_callback(message)
        self.logger.info(message)

    def update_config(self, config):
        if not config:
            self.enabled = False
            return
        
        # 优先从环境变量读取 API Key（安全性更高）
        import os
        env_key = os.environ.get('DEEPSEEK_API_KEY', '')
        
        self.enabled = config.get('enable', False)
        self.custom_prompt = config.get('prompt', '')
        self.timeout = config.get('timeout', 120)
        self.max_tokens = config.get('max_tokens', 300)
        self.temperature = config.get('temperature', 0.1)
        
        # ---- 解析当前使用的 Provider ----
        # 新版：多Provider配置模式
        providers_data = config.get('providers', [])
        active_id = config.get('active_provider_id', '')
        
        self.provider: AIProvider | None = None
        
        if providers_data:
            providers = [AIProvider(**p) if isinstance(p, dict) else p for p in providers_data]
            active = find_active_provider(providers, active_id)
            if active:
                self.provider = active
        
        # 回退到旧版单一配置
        if self.provider is None:
            old_key = env_key or config.get('api_key', '')
            old_url = config.get('base_url', 'https://api.deepseek.com/chat/completions').rstrip('/')
            old_model = config.get('model', 'deepseek-chat')
            if old_url or old_key:
                self.provider = AIProvider(
                    id="legacy",
                    name="Legacy",
                    provider_type="custom",
                    base_url=old_url,
                    api_key=old_key,
                    model=old_model,
                    models=[old_model],
                    enabled=True,
                )
        
        # 如果 provider 没有 key，才用环境变量回退（避免多 Provider 场景下错用 key）
        if env_key and self.provider and not self.provider.api_key:
            self.provider.api_key = env_key

    @property
    def api_key(self) -> str:
        return self.provider.api_key if self.provider else ""
    
    @property
    def base_url(self) -> str:
        return self.provider.base_url.rstrip('/') if self.provider else ""
    
    @property
    def model(self) -> str:
        return self.provider.model if self.provider else ""

    def check_relevance(self, title, content="", raise_on_error=False):
        """
        检查项目是否与高低压成套设备相关
        返回: (is_relevant: bool, reason: str)
        """
        if not self.enabled:
            return True, "AI未启用"

        if not self.provider:
            return True, "AI未配置Provider"
        
        if not self.provider.api_key:
            return True, "AI未配置Key"
        
        if not self.provider.base_url:
            return True, "AI未配置API地址"

        self.log(f"🤖 [AI分析] 开始分析: {title[:40]}...")

        system_prompt = get_ai_system_prompt(self.custom_prompt)
        user_content = f"项目标题: {title}\n项目内容: {content[:800]}"

        # 使用 ai_providers 的统一 payload 构建
        payload = build_request_payload(
            self.provider,
            system_prompt=system_prompt,
            user_content=user_content,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )

        # 直接使用用户提供的URL，不添加任何后缀
        url = self.provider.base_url.rstrip('/')

        self.log(f"🔗 [AI分析] 请求API: {self.provider.base_url}")
        self.log(f"📦 [AI分析] 使用模型: {self.provider.model}")
        self.log(f"🏷️  [AI分析] Provider: {self.provider.name}")

        try:
            import requests
            import time
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.provider.api_key}"
            }
            
            max_retries = 3
            retry_delay = 2  # 秒
            
            for attempt in range(max_retries):
                try:
                    self.log(f"⏳ [AI分析] 正在等待AI响应...")
                    resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
                    
                    if resp.status_code != 200:
                        error_detail = resp.text[:200]
                        self.log(f"❌ [AI分析] API返回错误: HTTP {resp.status_code}")
                        raise Exception(f"HTTP {resp.status_code}: {error_detail}")
                    
                    result = resp.json()
                    ai_content = parse_response(self.provider, result)
                    
                    self.log(f"✅ [AI分析] 收到AI响应")
                    
                    # 解析AI返回的JSON
                    try:
                        # 尝试从响应中提取JSON
                        if '```json' in ai_content:
                            json_str = ai_content.split('```json')[1].split('```')[0].strip()
                        elif '```' in ai_content:
                            json_str = ai_content.split('```')[1].split('```')[0].strip()
                        elif '{' in ai_content and '}' in ai_content:
                            start = ai_content.find('{')
                            end = ai_content.rfind('}') + 1
                            json_str = ai_content[start:end]
                        else:
                            json_str = ai_content
                            
                        analysis = json.loads(json_str)
                        is_relevant = analysis.get('relevant', False)
                        reason = analysis.get('reason', 'AI未提供理由')
                        
                        if is_relevant:
                            self.log(f"✅ [AI判定] 相关 - {reason}")
                        else:
                            self.log(f"🚫 [AI判定] 不相关 - {reason}")
                            
                        return is_relevant, reason
                        
                    except json.JSONDecodeError:
                        # 如果无法解析JSON，尝试从文本判断
                        self.log(f"⚠️ [AI分析] 返回非标准JSON，尝试文本分析")
                        is_relevant = "true" in ai_content.lower() or "相关" in ai_content or "是" in ai_content[:20]
                        return is_relevant, ai_content[:80]
                        
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                    # 网络连接错误或超时，可以重试
                    if attempt < max_retries - 1:
                        self.log(f"⚠️ [AI分析] 网络异常，{retry_delay}秒后重试 ({attempt + 1}/{max_retries})")
                        time.sleep(retry_delay)
                    else:
                        self.log(f"❌ [AI分析] 网络异常，已重试{max_retries}次仍失败")
                        if raise_on_error:
                            raise
                        return True, f"AI网络异常（已重试{max_retries}次）"

        except ImportError:
            self.log(f"❌ [AI分析] 缺少requests库")
            return True, "请安装 requests 库: pip install requests"
        except Exception as e:
            error_msg = str(e)
            self.log(f"❌ [AI分析] 请求失败: {error_msg[:100]}")
            self.logger.error(f"AI请求失败: {error_msg}")
            if raise_on_error:
                raise
            return True, f"AI请求异常: {error_msg[:50]}"
