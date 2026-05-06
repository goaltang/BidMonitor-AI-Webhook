# Commit Message 规范

> 本项目所有 Commit Message **统一使用中文**，禁止中英混杂。

---

## 格式

```
<type>(<scope>): <简短描述>

<可选：详细说明>
<可选：详细说明>
```

- `type` + `:` 后必须有一个空格
- `scope` 可选，用括号包裹
- 描述句尾**不加句号**

---

## Type 类型

| 类型 | 含义 | 使用场景 |
|------|------|---------|
| `feat` | 新功能 | 新增功能、新增模块、新增配置项 |
| `fix` | 修复 | 修复 Bug、修复逻辑错误、修复崩溃 |
| `docs` | 文档 | README、AGENTS.md、注释、帮助文本 |
| `style` | 格式 | 代码格式化、空行、缩进、分号（不影响逻辑） |
| `refactor` | 重构 | 重构代码结构、重命名变量、提取函数（无新功能无修复） |
| `perf` | 性能 | 优化性能、减少资源占用、加速查询 |
| `test` | 测试 | 新增/修改测试用例、测试框架调整 |
| `chore` | 杂项 | 构建脚本、依赖升级、目录整理、配置调整、代码无关的改动 |
| `revert` | 回滚 | 撤销之前的提交 |

---

## Scope 范围

| 范围 | 说明 |
|------|------|
| `gui` | Tkinter 桌面 GUI |
| `server` | FastAPI Web 服务端 |
| `domain` | 行业定义（词库、网站、提示词） |
| `crawler` | 爬虫模块 |
| `matcher` | 匹配引擎 |
| `notifier` | 通知模块（邮件/短信/微信/语音） |
| `ai` | AI Provider 管理 |
| `health` | 网站健康检测 |
| `config` | 配置管理 |
| `db` | 数据库/数据层 |
| `scripts` | 系统脚本 |
| `tools` | 分析工具 |
| `docs` | 文档 |

无明确范围时可省略括号。

---

## 正确示例

```
feat(domain): 新增化工企业采购平台分类

feat(gui): 添加网站源批量启用/禁用按钮

fix(crawler): 修复必联网反爬检测误判问题

refactor(ai): 统一 Provider 响应解析逻辑

docs: 更新 README 快速开始章节

chore: 升级 requests 到 2.32.0

chore: 整理根目录文件并创建 AGENTS.md 目录规范
```

---

## 错误示例

```
# ❌ 中英混杂
feat(domain): add chemical industry procurement sites

# ❌ 类型不对（新功能用 fix）
fix: 新增供应商门户爬虫

# ❌ 描述以句号结尾
feat(gui): 添加导出按钮。

# ❌ 缺少空格
feat(gui):添加导出按钮

# ❌ 过于模糊
fix: 修复 bug
```

---

## 多行提交

当改动涉及多个方面时，用 `-m` 分条说明：

```bash
git commit -m "feat(crawler): 添加军队采购网专用爬虫" \
  -m "- 支持分页抓取招标公告" \
  -m "- 集成反爬检测与指数退避重试" \
  -m "- 注册到爬虫注册表，ID 为 jungong"
```
