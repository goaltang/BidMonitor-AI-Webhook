"""
统一配置加载器

支持从 YAML / JSON 加载配置，自动搜索多个路径，合并行业默认值。
敏感配置（API Key、密码等）优先从环境变量或 .env 文件读取。
"""
import os
import json
from typing import Dict, Any, Optional

from .schema import AppConfig

# 尝试加载 .env 文件（如果存在）
try:
    from dotenv import load_dotenv
    _project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    _env_path = os.path.join(_project_root, '.env')
    if os.path.exists(_env_path):
        load_dotenv(_env_path, override=True)
except ImportError:
    pass


def _load_yaml(path: str) -> Optional[Dict[str, Any]]:
    """加载 YAML 文件"""
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        return None
    except FileNotFoundError:
        return None


def _load_json(path: str) -> Optional[Dict[str, Any]]:
    """加载 JSON 文件"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


def find_config_file(
    filename: str = "config.yaml",
    search_paths: Optional[list] = None,
) -> Optional[str]:
    """在多个路径中搜索配置文件
    
    搜索顺序：
    1. 当前工作目录
    2. 项目根目录（脚本所在目录的上级）
    3. 用户指定的路径
    """
    if search_paths is None:
        search_paths = [
            os.path.join("config", filename),
            os.path.join("..", "config", filename),
            filename,
        ]
    
    # 如果是绝对路径，直接检查
    if os.path.isabs(filename):
        return filename if os.path.exists(filename) else None
    
    # 尝试各个搜索路径
    for path in search_paths:
        if os.path.exists(path):
            return path
    
    # 尝试项目根目录
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for rel in [f"config/{filename}", filename]:
        full = os.path.join(script_dir, rel)
        if os.path.exists(full):
            return full
    
    return None


def load_config(
    path: Optional[str] = None,
    fill_defaults: bool = True,
) -> AppConfig:
    """加载应用配置
    
    配置加载优先级：
    1. 用户指定的 path
    2. user_config.json（GUI 用户配置，优先）
    3. config.yaml / config.yml（CLI/Server 配置）
    4. config.json
    
    Args:
        path: 配置文件路径，None 则自动搜索
        fill_defaults: 是否用行业默认值填充空字段
        
    Returns:
        AppConfig 对象
    """
    raw_data: Dict[str, Any] = {}
    
    if path:
        if path.endswith(".json"):
            raw_data = _load_json(path) or {}
        else:
            raw_data = _load_yaml(path) or {}
    else:
        # 优先搜索 user_config.json（GUI 配置为单一事实来源）
        user_config = find_config_file("user_config.json")
        if user_config:
            raw_data = _load_json(user_config) or {}
        
        # 回退到 YAML/JSON 配置
        if not raw_data:
            for ext in [".yaml", ".yml", ".json"]:
                found = find_config_file(f"config{ext}")
                if found:
                    if found.endswith(".json"):
                        raw_data = _load_json(found) or {}
                    else:
                        raw_data = _load_yaml(found) or {}
                    break
    
    config = AppConfig.from_legacy_dict(raw_data)
    
    # 用行业默认值填充空字段
    if fill_defaults:
        _fill_industry_defaults(config)
    
    return config


def _fill_industry_defaults(config: AppConfig) -> None:
    """用 domain.industry 的默认值填充空配置字段"""
    try:
        from domain.industry import (
            DEFAULT_INCLUDE_KEYWORDS,
            DEFAULT_EXCLUDE_KEYWORDS,
            DEFAULT_MUST_CONTAIN_KEYWORDS,
            DEFAULT_SEARCH_KEYWORDS,
        )
    except ImportError:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from domain.industry import (
            DEFAULT_INCLUDE_KEYWORDS,
            DEFAULT_EXCLUDE_KEYWORDS,
            DEFAULT_MUST_CONTAIN_KEYWORDS,
            DEFAULT_SEARCH_KEYWORDS,
        )
    
    if not config.industry.include:
        config.industry.include = DEFAULT_INCLUDE_KEYWORDS.copy()
    if not config.industry.exclude:
        config.industry.exclude = DEFAULT_EXCLUDE_KEYWORDS.copy()
    if not config.industry.must_contain:
        config.industry.must_contain = DEFAULT_MUST_CONTAIN_KEYWORDS.copy()
    if not config.industry.search_keywords:
        # 向后兼容：如果用户已配置过滤词但未配置搜索词，
        # 使用过滤词前3个作为搜索词（保持修改前行为）
        if config.industry.include:
            config.industry.search_keywords = config.industry.include[:3]
        else:
            config.industry.search_keywords = DEFAULT_SEARCH_KEYWORDS.copy()


def save_config(config: AppConfig, path: str) -> None:
    """保存配置到文件
    
    Args:
        config: 配置对象
        path: 保存路径（支持 .yaml / .json）
    """
    data = config.model_dump(mode="json", exclude_none=True)
    
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    
    if path.endswith(".json"):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        try:
            import yaml
            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False)
        except ImportError:
            # 没有 yaml 时 fallback 到 json
            json_path = path.replace(".yaml", ".json").replace(".yml", ".json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
