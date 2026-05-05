import json
import logging

try:
    from .domain.prompts import get_ai_system_prompt
except ImportError:
    from domain.prompts import get_ai_system_prompt


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
        self.api_key = env_key or config.get('api_key', '')
        self.base_url = config.get('base_url', 'https://cc.honoursoft.cn/').rstrip('/')
        self.model = config.get('model', 'claude-sonnet-4-5-20250929-thinking')
        self.enabled = config.get('enable', False)
        self.custom_prompt = config.get('prompt', '')

    def check_relevance(self, title, content="", raise_on_error=False):
        """
        检查项目是否与高低压成套设备相关
        返回: (is_relevant: bool, reason: str)
        """
        if not self.enabled:
            return True, "AI未启用"

        if not self.api_key:
            return True, "AI未配置Key"

        self.log(f"🤖 [AI分析] 开始分析: {title[:40]}...")

        system_prompt = get_ai_system_prompt(self.custom_prompt)

        user_content = f"项目标题: {title}\n项目内容: {content[:800]}"

        # 判断是否使用 Claude 原生格式（基于模型名称和URL）
        is_claude_native = (
            'claude' in self.model.lower() and 
            'honoursoft' in self.base_url.lower()
        )
        
        # 构造请求payload（自动兼容 Claude 和 OpenAI/DeepSeek 格式）
        if is_claude_native:
            # Claude 原生格式：system 作为顶级参数
            payload = {
                "model": self.model,
                "system": system_prompt,
                "messages": [
                    {"role": "user", "content": user_content}
                ],
                "temperature": 0.1,
                "max_tokens": 300
            }
        else:
            # OpenAI/DeepSeek 兼容格式：system 在 messages 数组中
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                "temperature": 0.1,
                "max_tokens": 300
            }

        # 直接使用用户提供的URL，不添加任何后缀
        url = self.base_url.rstrip('/')

        self.log(f"🔗 [AI分析] 请求API: {self.base_url}")
        self.log(f"📦 [AI分析] 使用模型: {self.model}")

        try:
            import requests
            import time
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            max_retries = 3
            retry_delay = 2  # 秒
            
            for attempt in range(max_retries):
                try:
                    self.log(f"⏳ [AI分析] 正在等待AI响应...")
                    resp = requests.post(url, headers=headers, json=payload, timeout=120)
                    
                    if resp.status_code != 200:
                        error_detail = resp.text[:200]
                        self.log(f"❌ [AI分析] API返回错误: HTTP {resp.status_code}")
                        raise Exception(f"HTTP {resp.status_code}: {error_detail}")
                    
                    result = resp.json()
                    ai_content = result['choices'][0]['message']['content']
                    
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
