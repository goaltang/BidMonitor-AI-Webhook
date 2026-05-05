"""
测试关键字匹配引擎
"""
import pytest
from matcher.keyword import KeywordMatcher, MatchResult


class TestKeywordMatcher:
    """KeywordMatcher 单元测试"""

    def test_basic_match(self):
        """基本匹配：包含任一关键词即匹配"""
        matcher = KeywordMatcher(include_keywords=["开关柜", "配电柜"])
        result = matcher.match("某项目采购高压开关柜设备")
        assert result.matched is True
        assert "开关柜" in result.matched_keywords

    def test_no_match(self):
        """不包含任何关键词时不匹配"""
        matcher = KeywordMatcher(include_keywords=["开关柜", "配电柜"])
        result = matcher.match("某项目采购办公家具")
        assert result.matched is False
        assert result.matched_keywords == []

    def test_exclude_keyword(self):
        """排除关键词：匹配排除词时返回不匹配"""
        matcher = KeywordMatcher(
            include_keywords=["开关柜"],
            exclude_keywords=["设计"]
        )
        result = matcher.match("某项目开关柜设计服务")
        assert result.matched is False
        assert result.excluded_by == "设计"

    def test_must_contain_match(self):
        """必须包含关键词：匹配 must_contain 中至少一个"""
        matcher = KeywordMatcher(
            include_keywords=["设备", "采购"],
            must_contain_keywords=["高压", "低压"]
        )
        result = matcher.match("某项目采购高压设备")
        assert result.matched is True

    def test_must_contain_fail(self):
        """必须包含关键词：未匹配 must_contain 时不匹配"""
        matcher = KeywordMatcher(
            include_keywords=["设备", "采购"],
            must_contain_keywords=["高压", "低压"]
        )
        result = matcher.match("某项目采购办公设备")
        assert result.matched is False

    def test_case_insensitive(self):
        """大小写不敏感"""
        matcher = KeywordMatcher(include_keywords=["开关柜"])
        result = matcher.match("某项目采购高压开关柜设备")
        assert result.matched is True
        result2 = matcher.match("某项目采购高压KaiGuan柜设备")
        assert result2.matched is False  # 只匹配完整词

    def test_empty_text(self):
        """空文本返回不匹配"""
        matcher = KeywordMatcher(include_keywords=["开关柜"])
        result = matcher.match("")
        assert result.matched is False
        result2 = matcher.match(None)
        assert result2.matched is False

    def test_match_any_multiple_texts(self):
        """match_any: 多个文本中任一匹配即可"""
        matcher = KeywordMatcher(include_keywords=["开关柜"])
        result = matcher.match_any("项目名称", "某项目采购高压开关柜设备")
        assert result.matched is True

    def test_match_any_excluded(self):
        """match_any: 任一文本被排除则整体不匹配"""
        matcher = KeywordMatcher(
            include_keywords=["开关柜"],
            exclude_keywords=["设计"]
        )
        result = matcher.match_any("项目名称", "某项目开关柜设计服务")
        assert result.matched is False
        assert result.excluded_by == "设计"

    def test_multiple_keywords_matched(self):
        """同时匹配多个关键词"""
        matcher = KeywordMatcher(include_keywords=["开关柜", "配电柜", "变压器"])
        result = matcher.match("某项目采购开关柜和配电柜")
        assert result.matched is True
        assert len(result.matched_keywords) == 2
        assert "开关柜" in result.matched_keywords
        assert "配电柜" in result.matched_keywords


class TestRegexMatcher:
    """RegexMatcher 单元测试"""

    def test_regex_match(self):
        """正则匹配成功"""
        from matcher.keyword import RegexMatcher
        matcher = RegexMatcher([r"KYN28[AB]?", r"GGD\d*"])
        assert matcher.match("项目采购KYN28A开关柜") is True
        assert matcher.match("项目采购GGD2配电柜") is True

    def test_regex_no_match(self):
        """正则匹配失败"""
        from matcher.keyword import RegexMatcher
        matcher = RegexMatcher([r"KYN28[AB]?"])
        assert matcher.match("项目采购MNS配电柜") is False

    def test_regex_empty_text(self):
        """空文本正则匹配失败"""
        from matcher.keyword import RegexMatcher
        matcher = RegexMatcher([r"KYN28"])
        assert matcher.match("") is False
        assert matcher.match(None) is False
