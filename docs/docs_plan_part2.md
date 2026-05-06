---

### Phase 3：批量扩展与优化（按需，长期）

| 任务 | 说明 |
|------|------|
| **3.1 逐个平台评估** | 剩余平台按"开发难度 × 业务价值"排序，逐个开发 |
| **3.2 复杂平台处理** | 需要 Selenium + 登录的平台，复用现有 `SeleniumCrawler` + 登录扩展 |
| **3.3 无法自动化的平台** | 保持"手动导入"，提供邮件转发自动解析、微信机器人接收等辅助手段 |
| **3.4 数据看板增强** | 增加统计图表（各平台信息量趋势、AI 过滤命中率、商机转化率等） |
| **3.5 数据导出** | 支持按时间 / 平台 / 关键词导出 Excel / PDF |

---

### Phase 4：代码质量（穿插进行）

| 任务 | 说明 |
|------|------|
| **4.1 gui.py 拆分** | 拆成 `src/gui/` 包，主窗口 + 独立对话框模块 |
| **4.2 测试覆盖** | 为 LoginCrawler、数据导入等新增模块补测试 |
| **4.3 文档更新** | README、部署文档、使用手册同步更新 |

---

## 四、关键技术方案

### 4.1 LoginCrawler 基类设计

```python
class LoginCrawler(BaseCrawler):
    def __init__(self, config, name, url, credentials=None):
        super().__init__(config, name, url)
        self.credentials = credentials  # {username, password}
        self.logged_in = False

    def login(self) -> bool:
        """子类必须实现：执行登录，返回是否成功"""
        raise NotImplementedError

    def is_session_valid(self) -> bool:
        """检测当前 Session 是否还有效"""
        pass

    def crawl(self, stop_event=None):
        if not self.logged_in:
            if not self.login():
                return None  # 登录失败，标记网站不可用
        return super().crawl(stop_event)
```

### 4.2 账号密码安全存储

- 存储位置：`user_config.json`（已存在，且被 Git 忽略）
- 加密方式：用系统生成的密钥对敏感字段做简单对称加密（如 Fernet）
- GUI 显示：密码框显示 `******`，编辑时传空不覆盖原值（已有这个逻辑）

### 4.3 手动导入数据格式

Excel/CSV 模板：

| 标题 | 链接 | 发布日期 | 平台来源 | 内容摘要 | 采购方 |
|------|------|---------|---------|---------|--------|

导入后走同样的流程：关键词匹配 → AI 过滤 → 去重 → 通知

---

## 五、风险评估与应对

| 风险 | 影响 | 应对 |
|------|------|------|
| 登录平台反爬升级 | 已开发的爬虫失效 | 健康检测发现异常，自动降级为手动导入 |
| CA 证书 / USBKey 平台无法自动化 | 这类平台约占 10-15% | 明确不支持，提供手动导入兜底 |
| 平台页面改版 | 解析逻辑失效 | 每个爬虫加版本检测，失效时告警 |
| 开发周期长，业务等不及 | 系统迟迟无法使用 | Phase 1 先做手动导入，立刻可用 |

---

## 六、下一步行动

1. **等业务人员反馈后，从 100+ 平台里选出最核心的 5-10 个**，评估哪些适合 Phase 2 试点自动爬取
2. **确认 Phase 1 先做手动导入 + 平台分类重构，是否同意？**
3. **gui.py 拆分放在 Phase 1 还是 Phase 4？**（Phase 1 拆的话，后面加新功能更清爽；Phase 4 拆的话，先聚焦业务功能）
