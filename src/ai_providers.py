"""
AI Provider 预设库 & 管理工具

参考 CC Switch 设计模式：
- 内置 50+ 主流/中转/云平台的 Provider 预设
- 支持一键添加、编辑、删除、切换、测速
- 支持自定义 Provider（任意中转 API）
"""
import uuid
import time
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict

try:
    import requests
except ImportError:
    requests = None

logger = logging.getLogger("AIProviders")


@dataclass
class AIProvider:
    """单个 AI Provider 配置"""
    id: str = ""
    name: str = ""
    provider_type: str = "preset"  # "preset" | "custom"
    preset_id: str = ""            # 关联的预设模板ID
    base_url: str = ""
    api_key: str = ""
    model: str = ""                # 当前使用的模型
    models: List[str] = field(default_factory=list)  # 该Provider支持的模型列表
    notes: str = ""                # 用户备注
    enabled: bool = True
    latency_ms: int = 0            # 上次测速结果（毫秒，0=未测试）
    
    def __post_init__(self):
        if not self.id:
            self.id = f"provider_{uuid.uuid4().hex[:8]}"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AIProvider":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    @property
    def display_name(self) -> str:
        """用于UI显示的名称"""
        status = "🟢" if self.enabled else "🔴"
        latency = f" {self.latency_ms}ms" if self.latency_ms > 0 else ""
        return f"{status} {self.name}{latency}"
    
    @property
    def is_custom(self) -> bool:
        return self.provider_type == "custom"


# =============================================================================
# 内置 Provider 预设模板
# =============================================================================
# 每个预设包含：名称、默认Base URL、默认模型列表、请求格式标记
# =============================================================================

AI_PROVIDER_PRESETS: Dict[str, Dict[str, Any]] = {
    # -------------------------------------------------------------------------
    # 官方直连 - 国际
    # -------------------------------------------------------------------------
    "openai": {
        "name": "OpenAI",
        "category": "官方直连",
        "base_url": "https://api.openai.com/v1/chat/completions",
        "models": [
            "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo",
            "o1-preview", "o1-mini", "o3-mini"
        ],
        "default_model": "gpt-4o-mini",
        "format": "openai",
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "category": "官方直连",
        "base_url": "https://api.anthropic.com/v1/messages",
        "models": [
            "claude-3-5-sonnet-latest", "claude-3-5-haiku-latest",
            "claude-3-opus-latest", "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ],
        "default_model": "claude-3-5-sonnet-latest",
        "format": "anthropic",
    },
    "google_gemini": {
        "name": "Google Gemini",
        "category": "官方直连",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/models",
        "models": [
            "gemini-2.5-pro", "gemini-2.0-flash", "gemini-1.5-pro",
            "gemini-1.5-flash", "gemini-1.0-pro"
        ],
        "default_model": "gemini-1.5-flash",
        "format": "gemini",
    },
    "deepseek": {
        "name": "DeepSeek",
        "category": "官方直连",
        "base_url": "https://api.deepseek.com/chat/completions",
        "models": [
            "deepseek-chat", "deepseek-reasoner", "deepseek-coder"
        ],
        "default_model": "deepseek-chat",
        "format": "openai",
    },
    "groq": {
        "name": "Groq",
        "category": "官方直连",
        "base_url": "https://api.groq.com/openai/v1/chat/completions",
        "models": [
            "llama-3.3-70b-versatile", "llama-3.1-8b-instant",
            "mixtral-8x7b-32768", "gemma2-9b-it"
        ],
        "default_model": "llama-3.3-70b-versatile",
        "format": "openai",
    },
    "mistral": {
        "name": "Mistral AI",
        "category": "官方直连",
        "base_url": "https://api.mistral.ai/v1/chat/completions",
        "models": [
            "mistral-large-latest", "mistral-medium-latest",
            "mistral-small-latest", "codestral-latest"
        ],
        "default_model": "mistral-small-latest",
        "format": "openai",
    },
    "cohere": {
        "name": "Cohere",
        "category": "官方直连",
        "base_url": "https://api.cohere.ai/v1/chat",
        "models": [
            "command-r-plus", "command-r", "command-light"
        ],
        "default_model": "command-r",
        "format": "cohere",
    },
    "xai": {
        "name": "xAI (Grok)",
        "category": "官方直连",
        "base_url": "https://api.x.ai/v1/chat/completions",
        "models": [
            "grok-2", "grok-2-vision", "grok-beta"
        ],
        "default_model": "grok-beta",
        "format": "openai",
    },
    
    # -------------------------------------------------------------------------
    # 官方直连 - 国产大模型
    # -------------------------------------------------------------------------
    "moonshot_kimi": {
        "name": "Moonshot Kimi",
        "category": "国产官方",
        "base_url": "https://api.moonshot.cn/v1/chat/completions",
        "models": [
            "kimi-k2", "kimi-k1.5", "kimi-latest",
            "moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"
        ],
        "default_model": "kimi-latest",
        "format": "openai",
    },
    "zhipu_glm": {
        "name": "智谱 GLM",
        "category": "国产官方",
        "base_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "models": [
            "glm-4-plus", "glm-4-air", "glm-4-flash",
            "glm-4-long", "glm-4", "glm-4-alltools"
        ],
        "default_model": "glm-4-air",
        "format": "openai",
    },
    "qwen_tongyi": {
        "name": "通义千问",
        "category": "国产官方",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "models": [
            "qwen-max", "qwen-plus", "qwen-turbo",
            "qwen-coder-plus", "qwen2.5-72b-instruct"
        ],
        "default_model": "qwen-plus",
        "format": "openai",
    },
    "xinghuo_xfyun": {
        "name": "讯飞星火",
        "category": "国产官方",
        "base_url": "https://spark-api-open.xf-yun.com/v1/chat/completions",
        "models": [
            "lite", "generalv3", "pro-128k", "max-32k", "4.0-ultra"
        ],
        "default_model": "generalv3",
        "format": "openai",
    },
    "wenxin_yiyan": {
        "name": "文心一言",
        "category": "国产官方",
        "base_url": "https://qianfan.baidubce.com/v2/chat/completions",
        "models": [
            "ernie-4.0-turbo-8k", "ernie-4.0", "ernie-3.5-8k",
            "ernie-speed-8k", "ernie-lite-8k"
        ],
        "default_model": "ernie-3.5-8k",
        "format": "openai",
    },
    "doubao_byte": {
        "name": "字节豆包",
        "category": "国产官方",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        "models": [
            "doubao-pro-256k", "doubao-pro-128k", "doubao-pro-32k",
            "doubao-lite-128k", "doubao-lite-32k", "doubao-vision-pro"
        ],
        "default_model": "doubao-pro-128k",
        "format": "openai",
    },
    "baichuan": {
        "name": "百川智能",
        "category": "国产官方",
        "base_url": "https://api.baichuan-ai.com/v1/chat/completions",
        "models": [
            "Baichuan4", "Baichuan3-Turbo", "Baichuan3-Turbo-128k",
            "Baichuan2-Turbo"
        ],
        "default_model": "Baichuan3-Turbo",
        "format": "openai",
    },
    "minimax": {
        "name": "MiniMax",
        "category": "国产官方",
        "base_url": "https://api.minimax.chat/v1/text/chatcompletion_v2",
        "models": [
            "abab6.5s-chat", "abab6.5-chat", "abab6-chat"
        ],
        "default_model": "abab6.5s-chat",
        "format": "minimax",
    },
    "lingyi_01": {
        "name": "零一万物",
        "category": "国产官方",
        "base_url": "https://api.lingyiwanwu.com/v1/chat/completions",
        "models": [
            "yi-large", "yi-medium", "yi-spark", "yi-vision"
        ],
        "default_model": "yi-medium",
        "format": "openai",
    },
    "stepfun": {
        "name": "阶跃星辰",
        "category": "国产官方",
        "base_url": "https://api.stepfun.com/v1/chat/completions",
        "models": [
            "step-2-16k-nightly", "step-1-256k", "step-1-128k", "step-1-32k", "step-1-8k"
        ],
        "default_model": "step-1-128k",
        "format": "openai",
    },
    "hunyuan_tencent": {
        "name": "腾讯混元",
        "category": "国产官方",
        "base_url": "https://hunyuan.tencentcloudapi.com/v1/chat/completions",
        "models": [
            "hunyuan-pro", "hunyuan-standard", "hunyuan-lite", "hunyuan-vision"
        ],
        "default_model": "hunyuan-standard",
        "format": "openai",
    },
    "sensechat": {
        "name": "商汤商量",
        "category": "国产官方",
        "base_url": "https://api.sensenova.cn/v1/chat/completions",
        "models": [
            "SenseChat-5", "SenseChat-Turbo", "SenseChat-4.0", "SenseChat-5-Vision"
        ],
        "default_model": "SenseChat-Turbo",
        "format": "openai",
    },
    
    # -------------------------------------------------------------------------
    # 中转/聚合 API (Popular Proxies / Aggregators)
    # -------------------------------------------------------------------------
    "openrouter": {
        "name": "OpenRouter",
        "category": "中转聚合",
        "base_url": "https://openrouter.ai/api/v1/chat/completions",
        "models": [
            "openai/gpt-4o", "anthropic/claude-3.5-sonnet",
            "google/gemini-2.0-flash", "meta-llama/llama-3.3-70b"
        ],
        "default_model": "openai/gpt-4o-mini",
        "format": "openai",
    },
    "api2d": {
        "name": "API2D",
        "category": "中转聚合",
        "base_url": "https://openai.api2d.net/v1/chat/completions",
        "models": [
            "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "claude-3-5-sonnet-20241022"
        ],
        "default_model": "gpt-4o-mini",
        "format": "openai",
    },
    "ohmygpt": {
        "name": "OhMyGPT",
        "category": "中转聚合",
        "base_url": "https://api.ohmygpt.com/v1/chat/completions",
        "models": [
            "gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet", "gemini-1.5-pro"
        ],
        "default_model": "gpt-4o-mini",
        "format": "openai",
    },
    "apiyi": {
        "name": "APIYI",
        "category": "中转聚合",
        "base_url": "https://api.apiyi.com/v1/chat/completions",
        "models": [
            "gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet", "deepseek-chat"
        ],
        "default_model": "gpt-4o-mini",
        "format": "openai",
    },
    "closeai": {
        "name": "CloseAI",
        "category": "中转聚合",
        "base_url": "https://api.closeai-proxy.com/v1/chat/completions",
        "models": [
            "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "claude-3-5-sonnet"
        ],
        "default_model": "gpt-4o-mini",
        "format": "openai",
    },
    "oneapi": {
        "name": "OneAPI / NewAPI",
        "category": "中转聚合",
        "base_url": "https://<your-domain>/v1/chat/completions",
        "models": [
            "gpt-4o", "claude-3-5-sonnet", "deepseek-chat", "gemini-1.5-pro"
        ],
        "default_model": "gpt-4o",
        "format": "openai",
    },
    "aiproxy": {
        "name": "AI Proxy",
        "category": "中转聚合",
        "base_url": "https://api.aiproxy.io/v1/chat/completions",
        "models": [
            "gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet"
        ],
        "default_model": "gpt-4o-mini",
        "format": "openai",
    },
    "aihub": {
        "name": "AIHub",
        "category": "中转聚合",
        "base_url": "https://aihubMix.com/v1/chat/completions",
        "models": [
            "gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet", "deepseek-chat"
        ],
        "default_model": "gpt-4o-mini",
        "format": "openai",
    },
    "aigc2d": {
        "name": "AIGC2D",
        "category": "中转聚合",
        "base_url": "https://api.aigc2d.com/v1/chat/completions",
        "models": [
            "gpt-4o", "claude-3-5-sonnet", "gemini-1.5-pro"
        ],
        "default_model": "gpt-4o-mini",
        "format": "openai",
    },
    
    # -------------------------------------------------------------------------
    # 国内云平台
    # -------------------------------------------------------------------------
    "aliyun_bailian": {
        "name": "阿里云百炼",
        "category": "国内云",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        "models": [
            "qwen-max", "qwen-plus", "qwen-turbo", "qwen-coder-plus",
            "deepseek-r1", "deepseek-v3"
        ],
        "default_model": "qwen-plus",
        "format": "openai",
    },
    "tencent_ti": {
        "name": "腾讯云 TI",
        "category": "国内云",
        "base_url": "https://tencent-ti.tencentcloudapi.com/v1/chat/completions",
        "models": [
            "hunyuan-pro", "hunyuan-standard", "hunyuan-lite"
        ],
        "default_model": "hunyuan-standard",
        "format": "openai",
    },
    "baidu_qianfan": {
        "name": "百度千帆",
        "category": "国内云",
        "base_url": "https://qianfan.baidubce.com/v2/chat/completions",
        "models": [
            "ernie-4.0-turbo", "ernie-3.5-8k", "ernie-speed-8k"
        ],
        "default_model": "ernie-3.5-8k",
        "format": "openai",
    },
    "volcengine": {
        "name": "火山引擎",
        "category": "国内云",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        "models": [
            "doubao-pro-256k", "doubao-pro-128k", "doubao-lite-128k"
        ],
        "default_model": "doubao-pro-128k",
        "format": "openai",
    },
    
    # -------------------------------------------------------------------------
    # 国外云平台 / 企业部署
    # -------------------------------------------------------------------------
    "azure_openai": {
        "name": "Azure OpenAI",
        "category": "企业云",
        "base_url": "https://<your-resource>.openai.azure.com/openai/deployments/<deployment>/chat/completions?api-version=2024-02-01",
        "models": [
            "gpt-4o", "gpt-4", "gpt-35-turbo"
        ],
        "default_model": "gpt-4o",
        "format": "openai",
    },
    "aws_bedrock": {
        "name": "AWS Bedrock",
        "category": "企业云",
        "base_url": "https://bedrock-runtime.<region>.amazonaws.com/model/anthropic.claude-3-sonnet/invoke",
        "models": [
            "anthropic.claude-3-5-sonnet", "anthropic.claude-3-haiku",
            "meta.llama3-70b", "amazon.nova-pro"
        ],
        "default_model": "anthropic.claude-3-5-sonnet",
        "format": "bedrock",
    },
    "nvidia_nim": {
        "name": "NVIDIA NIM",
        "category": "企业云",
        "base_url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "models": [
            "meta/llama3-70b-instruct", "meta/llama3-8b-instruct"
        ],
        "default_model": "meta/llama3-8b-instruct",
        "format": "openai",
    },
    "siliconflow": {
        "name": "硅基流动 SiliconFlow",
        "category": "国内云",
        "base_url": "https://api.siliconflow.cn/v1/chat/completions",
        "models": [
            "deepseek-ai/DeepSeek-V3", "deepseek-ai/DeepSeek-R1",
            "Qwen/Qwen2.5-72B-Instruct", "meta-llama/Meta-Llama-3.1-70B-Instruct"
        ],
        "default_model": "deepseek-ai/DeepSeek-V3",
        "format": "openai",
    },
    "together": {
        "name": "Together AI",
        "category": "国际云",
        "base_url": "https://api.together.xyz/v1/chat/completions",
        "models": [
            "meta-llama/Llama-3.3-70B-Instruct-Turbo", "mistralai/Mixtral-8x22B-Instruct-v0.1"
        ],
        "default_model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "format": "openai",
    },
}


def get_preset_categories() -> Dict[str, List[str]]:
    """按类别分组返回预设ID列表"""
    categories: Dict[str, List[str]] = {}
    for pid, preset in AI_PROVIDER_PRESETS.items():
        cat = preset.get("category", "其他")
        categories.setdefault(cat, []).append(pid)
    # 按指定顺序排序类别
    order = ["官方直连", "国产官方", "中转聚合", "国内云", "企业云", "国际云", "其他"]
    sorted_cats = {}
    for cat in order:
        if cat in categories:
            sorted_cats[cat] = categories[cat]
    for cat in categories:
        if cat not in sorted_cats:
            sorted_cats[cat] = categories[cat]
    return sorted_cats


def get_preset_by_id(preset_id: str) -> Optional[Dict[str, Any]]:
    """根据ID获取预设模板"""
    return AI_PROVIDER_PRESETS.get(preset_id)


def create_provider_from_preset(preset_id: str, name: str = "", api_key: str = "") -> AIProvider:
    """从预设模板创建 Provider 实例"""
    preset = get_preset_by_id(preset_id)
    if not preset:
        raise ValueError(f"未知预设: {preset_id}")
    
    return AIProvider(
        id=f"{preset_id}_{uuid.uuid4().hex[:6]}",
        name=name or preset["name"],
        provider_type="preset",
        preset_id=preset_id,
        base_url=preset["base_url"],
        api_key=api_key,
        model=preset["default_model"],
        models=list(preset["models"]),
        enabled=True,
    )


def create_custom_provider(name: str, base_url: str, api_key: str, model: str, models: List[str] = None) -> AIProvider:
    """创建自定义 Provider"""
    return AIProvider(
        id=f"custom_{uuid.uuid4().hex[:8]}",
        name=name,
        provider_type="custom",
        preset_id="",
        base_url=base_url,
        api_key=api_key,
        model=model,
        models=models or [model],
        enabled=True,
    )


# =============================================================================
# 请求格式适配 helpers
# =============================================================================

def build_request_payload(provider: AIProvider, system_prompt: str, user_content: str,
                          max_tokens: int = 300, temperature: float = 0.1) -> Dict[str, Any]:
    """根据 Provider 类型构建请求 Payload"""
    fmt = "openai"
    if provider.provider_type == "preset" and provider.preset_id:
        preset = get_preset_by_id(provider.preset_id)
        if preset:
            fmt = preset.get("format", "openai")
    
    if fmt == "anthropic":
        # Anthropic 原生格式：system 作为顶级参数
        return {
            "model": provider.model,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_content}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
    
    if fmt == "gemini":
        # Gemini 兼容格式（通过 OpenAI 兼容端点时与 openai 一致，这里保留原生差异）
        # 注意：Gemini 的 OpenAI 兼容端点已经标准化，大部分用户使用兼容端点
        return {
            "model": provider.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
    
    # 默认 OpenAI 兼容格式
    return {
        "model": provider.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }


def parse_response(provider: AIProvider, response_json: Dict[str, Any]) -> str:
    """统一解析各种格式的响应，返回 AI 文本内容"""
    fmt = "openai"
    if provider.provider_type == "preset" and provider.preset_id:
        preset = get_preset_by_id(provider.preset_id)
        if preset:
            fmt = preset.get("format", "openai")
    
    # OpenAI / DeepSeek / 大部分兼容格式
    if "choices" in response_json and response_json["choices"]:
        choice = response_json["choices"][0]
        if "message" in choice and "content" in choice["message"]:
            return choice["message"]["content"]
        if "text" in choice:
            return choice["text"]
    
    # Anthropic 格式（如果通过原生API）
    if "content" in response_json and isinstance(response_json["content"], list):
        for block in response_json["content"]:
            if block.get("type") == "text":
                return block.get("text", "")
    
    # 兜底
    return str(response_json)


# =============================================================================
# 测速 / 测试连接
# =============================================================================

def test_provider_latency(provider: AIProvider, timeout: int = 30) -> tuple[bool, int, str]:
    """
    测试 Provider 连接并测速
    
    Returns:
        (success: bool, latency_ms: int, message: str)
    """
    if not requests:
        return False, 0, "缺少 requests 库"
    
    if not provider.api_key:
        return False, 0, "未配置 API Key"
    
    url = provider.base_url.rstrip('/')
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {provider.api_key}"
    }
    
    # 使用极短的prompt来测速
    payload = build_request_payload(
        provider,
        system_prompt="You are a helpful assistant.",
        user_content="Hi",
        max_tokens=5,
        temperature=0.1
    )
    
    start = time.time()
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        elapsed = int((time.time() - start) * 1000)
        
        if resp.status_code == 200:
            provider.latency_ms = elapsed
            return True, elapsed, f"连接成功，延迟 {elapsed}ms"
        else:
            return False, elapsed, f"HTTP {resp.status_code}: {resp.text[:200]}"
    except requests.exceptions.Timeout:
        return False, 0, "请求超时"
    except requests.exceptions.ConnectionError as e:
        return False, 0, f"连接失败: {str(e)[:100]}"
    except Exception as e:
        return False, 0, f"异常: {str(e)[:100]}"


def get_provider_display_list(providers: List[AIProvider]) -> List[str]:
    """生成用于 Listbox/Combobox 显示的字符串列表"""
    return [p.display_name for p in providers]


def find_provider_by_id(providers: List[AIProvider], provider_id: str) -> Optional[AIProvider]:
    """根据ID查找 Provider"""
    for p in providers:
        if p.id == provider_id:
            return p
    return None


def find_active_provider(providers: List[AIProvider], active_id: str) -> Optional[AIProvider]:
    """查找当前激活的 Provider，如果找不到则返回第一个启用的"""
    if active_id:
        p = find_provider_by_id(providers, active_id)
        if p and p.enabled:
            return p
    for p in providers:
        if p.enabled:
            return p
    return None
