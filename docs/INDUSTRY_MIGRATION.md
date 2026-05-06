# 行业切换指南

本文档说明如何将 BidMonitor 招标监控系统从当前行业（高低压成套设备）快速适配到其他行业。

---

## 核心原则

重构后的系统采用**"行业定义层"**架构，行业相关的所有配置集中管理在 `src/domain/` 目录下。切换行业时，**主要修改此目录下的 3 个文件即可**。

```
src/domain/
├── industry.py    # 行业词库、默认关键词
├── sites.py       # 监控网站列表
└── prompts.py     # AI 筛选提示词
```

---

## 切换步骤（以"变压器行业"为例）

### 步骤 1：修改行业词库（`src/domain/industry.py`）

打开 `src/domain/industry.py`，修改以下常量：

```python
# 1. 行业名称
INDUSTRY_NAME = "变压器"

# 2. 产品词库（供AI、关键词匹配、爬虫搜索共用）
PRODUCT_KEYWORDS = [
    "油浸式变压器", "干式变压器", "箱式变压器",
    "电力变压器", "配电变压器", "特种变压器",
    "S11", "S13", "SCB10", "SCB13",
    "变压器成套设备", "变压器壳体", "变压器油",
]

# 3. 产品分类（用于AI理解业务边界）
PRODUCT_CATEGORIES = {
    "油浸式变压器": ["S11", "S13", "S20", "S22"],
    "干式变压器": ["SCB10", "SCB13", "SCB18"],
    "箱式变压器": ["欧式箱变", "美式箱变"],
}

# 4. 默认监控关键词
DEFAULT_INCLUDE_KEYWORDS = [
    "变压器", "电力变压器", "配电变压器",
    "干式变压器", "油浸式变压器", "箱式变压器",
    "S11", "S13", "SCB10", "SCB13",
]

# 5. 排除关键词
DEFAULT_EXCLUDE_KEYWORDS = [
    "设计", "监理", "咨询", "清洗", "运输",
    "仅施工", "劳务分包",
]

# 6. 爬虫默认搜索关键词
DEFAULT_SEARCH_KEYWORDS = [
    "变压器", "电力变压器", "配电变压器",
    "干式变压器", "油浸式变压器",
]
```

### 步骤 2：调整监控网站（`src/domain/sites.py`）

根据目标行业的特点，增删监控网站：

```python
def get_default_sites() -> Dict[str, Dict[str, str]]:
    return {
        # === 通用招标平台 ===
        'chinabidding': {'name': '中国采购与招标网', 'url': 'http://www.chinabidding.cn/'},
        # ...（保留通用平台）
        
        # === 电网公司（变压器核心客户）===
        'sgcc': {'name': '国家电网', 'url': 'https://ecp.sgcc.com.cn/'},
        
        # === 新增：变压器行业专用平台 ===
        'cepee': {'name': '中国电力设备信息网', 'url': 'http://www.cepee.com/'},
        # ...
    }
```

> **提示**：如果某个网站不适用于新行业，直接删除即可；如果需要新增，按上述格式添加。

### 步骤 3：修改 AI 提示词（`src/domain/prompts.py`）

修改 `get_ai_system_prompt()` 中的行业描述和判断条件：

```python
def get_ai_system_prompt(custom_prompt=None):
    if custom_prompt:
        return custom_prompt
    
    return (
        "你是一个专业的招投标项目筛选专家。我们公司是做【变压器】的，"
        "产品包括油浸式变压器（S11、S13等）、干式变压器（SCB10、SCB13等）、"
        "箱式变压器、电力变压器、配电变压器等。\n\n"
        "【符合条件】：\n"
        "- 变压器设备的采购或招标\n"
        "- 变电站配套变压器采购\n"
        "...\n\n"
        "【排除条件】：\n"
        "- 单纯的电线电缆、开关柜（非变压器）\n"
        "- 变压器维修、保养服务（非设备采购）\n"
        "...\n\n"
        "返回JSON: {...}"
    )
```

### 步骤 4：清空历史数据（建议）

切换行业后，旧行业的历史招标数据不再相关，建议清空：

```bash
# 删除 SQLite 数据库
rm data/bids.db

# 或启动系统后在 GUI / Web 界面中点击"清空历史"
```

### 步骤 5：重启系统验证

```bash
# 命令行模式
python run.py --crawl-once

# 或启动 GUI
python run.py

# 或启动服务端
python server/app.py
```

---

## 验证清单

切换行业后，按以下清单验证：

- [ ] `src/domain/industry.py` 中的 `INDUSTRY_NAME` 已更新
- [ ] `DEFAULT_INCLUDE_KEYWORDS` 包含新行业的核心产品词
- [ ] `DEFAULT_EXCLUDE_KEYWORDS` 排除了新行业不需要的业务类型
- [ ] `src/domain/sites.py` 中的网站列表适用于新行业
- [ ] `src/domain/prompts.py` 中的 AI 提示词描述了新行业产品
- [ ] 启动系统后，默认关键词显示正确
- [ ] 运行一次监控，抓取的内容与新行业相关
- [ ] 测试邮件/通知中的标题和描述符合新行业

---

## 常见问题

### Q1：需要修改爬虫代码吗？

**不需要**。爬虫只负责抓取页面链接，关键词过滤由 `KeywordMatcher` 统一处理。只要 `domain/industry.py` 中的关键词正确，爬虫会自动抓取相关内容。

### Q2：需要修改 `server/app.py` 或 `main.py` 吗？

**不需要**。这些入口文件已从 `domain` 模块动态读取默认值，修改 `domain/` 下的文件即可自动生效。

### Q3：如何快速测试新行业的关键词是否有效？

运行单元测试中的匹配器测试，替换为行业关键词：

```python
# tests/test_matcher.py 中临时修改
matcher = KeywordMatcher(include_keywords=["变压器", "电力变压器"])
result = matcher.match("某项目采购干式变压器设备")
assert result.matched is True
```

或直接启动系统跑一次监控，观察日志中的匹配结果。

### Q4：想保留多个行业配置怎么办？

可以创建多个行业配置文件，启动时动态加载：

```python
# src/domain/industries/
# ├── hv_equipment.py   # 高低压成套设备（默认）
# ├── transformer.py    # 变压器
# └── cable.py          # 电线电缆
```

然后在 `src/domain/__init__.py` 中通过环境变量切换：

```python
import os
industry_module = os.environ.get("BIDMONITOR_INDUSTRY", "industry")
```

---

## 附录：行业切换对比

| 项目 | 改造前（阶段一之前） | 改造后（当前） |
|------|-------------------|--------------|
| 修改文件数 | 10+ 个文件 | **3 个文件** |
| 修改位置 | 散落在代码各处 | 集中在 `src/domain/` |
| 关键词修改 | 改 9 个爬虫 + 2 个入口 + AI | 改 `industry.py` 一处 |
| 网站增删 | 改 `monitor_core.py` | 改 `sites.py` 一处 |
| AI 提示词 | 改 `ai_guard.py` | 改 `prompts.py` 一处 |
| 易错点 | 容易遗漏某个文件 | 结构清晰，不易遗漏 |

---

*如需更多帮助，请查看项目根目录的 `README.md` 或提交 Issue。*
