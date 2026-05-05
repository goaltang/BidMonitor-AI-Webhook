"""
测试配置系统
"""
import pytest
import json
import tempfile
import os

from config.schema import AppConfig, IndustryConfig, CrawlerConfig, EmailConfig
from config.loader import _fill_industry_defaults, find_config_file


class TestAppConfig:
    """AppConfig 数据模型测试"""

    def test_from_legacy_dict_nested(self):
        """兼容嵌套字典格式的旧配置"""
        legacy = {
            "keywords": {
                "include": ["开关柜", "配电柜"],
                "exclude": ["设计"],
                "must_contain": ["高压"]
            },
            "crawler": {
                "enabled_sites": ["ccgp", "chinabidding"],
                "use_selenium": True
            },
            "email": {
                "smtp_server": "smtp.qq.com",
                "smtp_port": 465,
                "sender": "test@qq.com",
                "password": "secret",
                "receiver": "test@qq.com"
            }
        }
        config = AppConfig.from_legacy_dict(legacy)
        assert config.industry.include == ["开关柜", "配电柜"]
        assert config.industry.exclude == ["设计"]
        assert config.industry.must_contain == ["高压"]
        assert config.crawler.enabled_sites == ["ccgp", "chinabidding"]
        assert config.crawler.use_selenium is True
        assert config.email.smtp_server == "smtp.qq.com"

    def test_from_legacy_dict_flat(self):
        """兼容扁平字符串格式的旧配置（server/app.py 格式）"""
        legacy = {
            "keywords": "开关柜,配电柜,箱变",
            "exclude": "设计,监理",
            "must_contain": "高压",
        }
        config = AppConfig.from_legacy_dict(legacy)
        assert "开关柜" in config.industry.include
        assert "配电柜" in config.industry.include
        assert "设计" in config.industry.exclude
        assert "高压" in config.industry.must_contain

    def test_from_legacy_dict_list_keywords(self):
        """兼容列表格式的关键词"""
        legacy = {
            "keywords": ["开关柜", "配电柜"],
        }
        config = AppConfig.from_legacy_dict(legacy)
        assert config.industry.include == ["开关柜", "配电柜"]

    def test_default_values(self):
        """默认值测试"""
        config = AppConfig()
        assert config.crawler.timeout == 30
        assert config.crawler.request_delay == 5
        assert config.crawler.max_retries == 3
        assert config.schedule.interval_minutes == 30
        assert config.ai.model == "deepseek-chat"

    def test_model_dump(self):
        """序列化测试"""
        config = AppConfig(
            industry=IndustryConfig(include=["开关柜"]),
            crawler=CrawlerConfig(enabled_sites=["ccgp"])
        )
        data = config.model_dump(mode="json")
        assert data["industry"]["include"] == ["开关柜"]
        assert data["crawler"]["enabled_sites"] == ["ccgp"]


class TestConfigLoader:
    """配置加载器测试"""

    def test_fill_industry_defaults(self):
        """填充行业默认值"""
        config = AppConfig()
        assert config.industry.include == []  # 加载前为空
        _fill_industry_defaults(config)
        assert len(config.industry.include) > 0
        assert "高低压成套设备" in config.industry.include
        assert len(config.industry.exclude) > 0

    def test_find_config_file_not_found(self):
        """找不到配置文件时返回 None"""
        result = find_config_file("nonexistent.yaml", search_paths=["/tmp/nonexistent"])
        assert result is None

    def test_load_yaml_file(self):
        """从 YAML 文件加载配置"""
        from config.loader import load_config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write("keywords:\n  include:\n    - 开关柜\n    - 配电柜\n")
            temp_path = f.name
        try:
            config = load_config(temp_path, fill_defaults=False)
            assert config.industry.include == ["开关柜", "配电柜"]
        finally:
            os.unlink(temp_path)

    def test_load_json_file(self):
        """从 JSON 文件加载配置"""
        from config.loader import load_config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump({"keywords": "开关柜,配电柜", "interval": 60}, f)
            temp_path = f.name
        try:
            config = load_config(temp_path, fill_defaults=False)
            assert "开关柜" in config.industry.include
            assert config.schedule.interval_minutes == 60
        finally:
            os.unlink(temp_path)
