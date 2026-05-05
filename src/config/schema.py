"""
配置数据模型 - Pydantic v2

统一所有入口（CLI / GUI / Server）的配置结构，提供类型校验和默认值。
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class CrawlerConfig(BaseModel):
    """爬虫配置"""
    enabled_sites: List[str] = Field(default_factory=list, description="启用的网站列表")
    custom_sites: List[Dict[str, str]] = Field(default_factory=list, description="用户自定义网站")
    use_selenium: bool = Field(default=False, description="是否使用Selenium浏览器模式")
    timeout: int = Field(default=30, description="请求超时（秒）")
    request_delay: int = Field(default=5, description="请求间隔（秒）")
    max_retries: int = Field(default=3, description="最大重试次数")


class EmailConfig(BaseModel):
    """邮件配置"""
    smtp_server: str = Field(default="smtp.qq.com")
    smtp_port: int = Field(default=465)
    use_ssl: bool = Field(default=True)
    sender: str = Field(default="", description="发件人邮箱")
    password: str = Field(default="", description="邮箱授权码/密码")
    receiver: str = Field(default="", description="收件人邮箱")


class SMSConfig(BaseModel):
    """短信配置"""
    provider: str = Field(default="aliyun", description="aliyun / tencent")
    access_key_id: str = Field(default="")
    access_key_secret: str = Field(default="")
    sign_name: str = Field(default="")
    template_code: str = Field(default="")


class VoiceConfig(BaseModel):
    """语音通知配置"""
    provider: str = Field(default="aliyun")
    access_key_id: str = Field(default="")
    access_key_secret: str = Field(default="")
    called_show_number: str = Field(default="")
    tts_code: str = Field(default="")


class WeChatConfig(BaseModel):
    """微信推送配置"""
    provider: str = Field(default="pushplus")
    token: str = Field(default="")


class AIConfig(BaseModel):
    """AI 过滤配置"""
    enable: bool = Field(default=False)
    base_url: str = Field(default="https://api.deepseek.com/chat/completions")
    api_key: str = Field(default="")
    model: str = Field(default="deepseek-chat")
    prompt: str = Field(default="", description="自定义AI系统提示词")


class ScheduleConfig(BaseModel):
    """定时任务配置"""
    interval_minutes: int = Field(default=30, description="监控间隔（分钟）")
    run_immediately: bool = Field(default=True, description="启动时是否立即执行一次")


class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = Field(default="INFO")
    file: Optional[str] = Field(default=None)


class Contact(BaseModel):
    """联系人"""
    name: str = Field(default="")
    email: str = Field(default="")
    email_password: str = Field(default="")
    email_type: str = Field(default="QQ邮箱")
    phone: str = Field(default="")
    wechat_token: str = Field(default="")
    enabled: bool = Field(default=True)


class IndustryConfig(BaseModel):
    """行业关键词配置（运行时从 domain.industry 填充）"""
    include: List[str] = Field(default_factory=list, description="包含关键词（OR）")
    exclude: List[str] = Field(default_factory=list, description="排除关键词")
    must_contain: List[str] = Field(default_factory=list, description="必须包含关键词（AND）")


class AppConfig(BaseModel):
    """应用总配置"""
    industry: IndustryConfig = Field(default_factory=IndustryConfig)
    crawler: CrawlerConfig = Field(default_factory=CrawlerConfig)
    email: Optional[EmailConfig] = Field(default=None)
    sms: Optional[SMSConfig] = Field(default=None)
    voice: Optional[VoiceConfig] = Field(default=None)
    wechat: Optional[WeChatConfig] = Field(default=None)
    ai: AIConfig = Field(default_factory=AIConfig)
    schedule: ScheduleConfig = Field(default_factory=ScheduleConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    contacts: List[Contact] = Field(default_factory=list)
    notify_method: str = Field(default="email", description="通知方式: email/sms/both")

    @classmethod
    def from_legacy_dict(cls, data: Dict[str, Any]) -> "AppConfig":
        """从旧版字典配置（兼容 YAML/JSON 两种格式）转换为新配置对象
        
        旧版配置结构可能为：
        - keywords: {include: [...], exclude: [...]}
        - crawler: {...}
        - email: {...}
        - schedule: {...}
        """
        kwargs: Dict[str, Any] = {}
        
        # 行业关键词（兼容两种格式）
        keywords_data = data.get("keywords", {})
        if isinstance(keywords_data, dict):
            kwargs["industry"] = IndustryConfig(
                include=keywords_data.get("include", []),
                exclude=keywords_data.get("exclude", []),
                must_contain=keywords_data.get("must_contain", []),
            )
        elif isinstance(keywords_data, list):
            kwargs["industry"] = IndustryConfig(include=keywords_data)
        
        # 爬虫配置
        if "crawler" in data:
            kwargs["crawler"] = CrawlerConfig(**data["crawler"])
        
        # 通知配置
        if "email" in data:
            kwargs["email"] = EmailConfig(**data["email"])
        if "sms" in data:
            kwargs["sms"] = SMSConfig(**data["sms"])
        if "voice" in data:
            kwargs["voice"] = VoiceConfig(**data["voice"])
        if "wechat" in data:
            kwargs["wechat"] = WeChatConfig(**data["wechat"])
        
        # AI 配置（兼容 ai_config 和 ai 两种 key）
        ai_data = data.get("ai") or data.get("ai_config", {})
        if ai_data:
            kwargs["ai"] = AIConfig(**ai_data)
        
        # 定时任务（兼容 schedule 和 scheduler）
        schedule_data = data.get("schedule") or data.get("scheduler", {})
        if schedule_data:
            kwargs["schedule"] = ScheduleConfig(**schedule_data)
        
        # 日志
        if "logging" in data:
            kwargs["logging"] = LoggingConfig(**data["logging"])
        
        # 联系人
        if "contacts" in data:
            kwargs["contacts"] = [Contact(**c) for c in data["contacts"]]
        
        # 通知方式
        if "notify_method" in data:
            kwargs["notify_method"] = data["notify_method"]
        
        return cls(**kwargs)
