# AGENTS.md — BidMonitor AI 项目目录规范

> 本文档供 AI Agent 编写/创建文件时参考，确保根目录保持整洁。

---

## 📁 目录速查表

| 目录 | 用途 | 什么文件放这里 | 什么文件**不要**放这里 |
|------|------|---------------|----------------------|
| `src/` | 核心源码 | 业务逻辑、爬虫、通知、匹配、调度、配置管理、GUI | 临时脚本、日志、文档 |
| `server/` | Web 服务端 | FastAPI 应用、静态资源、部署脚本 | 爬虫逻辑、分析脚本 |
| `scripts/` | 系统级脚本 | `pack.bat`、`verify_system.py` 等随项目长期维护的脚本 | 一次性分析脚本 |
| `config/` | 配置模板 | `config.yaml` 等非敏感配置 | 敏感信息（放 `.env`） |
| `data/` | 持久化数据 | SQLite 数据库 `.db` | 临时 HTML/抓取的页面 |
| `tests/` | 测试代码 | `pytest` 测试文件 | 非测试代码 |
| **`tools/`** | **分析/诊断工具** | **一次性或临时性的分析脚本**，如 `analyze_*.py`、`update_all_sites.py` | 核心功能代码 |
| **`logs/`** | **日志与输出** | **运行日志、分析报告、程序输出 `.txt/.json`** | 源码、HTML 原始数据 |
| **`tmp/`** | **临时数据** | **抓取的原始 HTML、临时 `.txt` 数据、缓存文件** | 需长期保留的文件 |
| **`docs/`** | **文档** | **规划文档、迁移指南、设计文档 `.md`** | 代码文件 |

---

## 🚫 根目录禁止清单

根目录**只保留**以下核心文件，其余一律归入子目录：

```
BidMonitor-AI-Webhook/
├── src/              # 核心源码
├── server/           # Web 服务端
├── scripts/          # 系统级脚本
├── config/           # 配置
├── data/             # 数据库
├── tests/            # 测试
├── tools/            # 一次性分析工具
├── logs/             # 日志输出
├── tmp/              # 临时数据
├── docs/             # 文档
├── run.py            # 桌面版入口（保留根目录）
├── requirements.txt  # 依赖列表
├── .env / .env.example
├── .gitignore
└── README.md
```

**以下类型文件禁止直接放在根目录：**

| 文件类型 | 正确位置 | 示例 |
|---------|---------|------|
| 一次性分析脚本 | `tools/` | `analyze_*.py`, `update_all_sites.py` |
| 运行日志/输出 | `logs/` | `output_log.txt`, `analyze_report.txt` |
| 抓取的原始 HTML | `tmp/` | `xaprtc.html`, `minmetals.html` |
| 临时数据 `.txt/.json` | `tmp/` 或 `logs/` | `xaprtc_links.txt`, `analyze_result.json` |
| 规划/设计文档 | `docs/` | `docs_plan.md`, `INDUSTRY_MIGRATION.md` |

---

## ✅ 创建新文件时的判断流程

```
1. 这是核心功能代码？
   → 放入 src/ 的对应子模块

2. 这是 Web 服务端代码？
   → 放入 server/

3. 这是长期维护的系统脚本？
   → 放入 scripts/

4. 这是一次性分析/诊断/辅助工具？
   → 放入 tools/

5. 这是日志或程序输出？
   → 放入 logs/

6. 这是抓取的原始页面或临时数据？
   → 放入 tmp/

7. 这是文档、规划、迁移说明？
   → 放入 docs/

8. 这是测试代码？
   → 放入 tests/

9. 都不属于以上？
   → 先放 tools/（代码）或 tmp/（数据），并在代码注释中说明用途
```

---

## 📝 路径引用规范

若脚本需要读写项目内其他目录的文件，**禁止使用硬编码相对路径**（如 `'./analyze_result.json'`）。

推荐做法：

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # 项目根目录

# 读取/写入示例
with open(BASE_DIR / 'logs' / 'output.txt', 'w', encoding='utf-8') as f:
    f.write(data)
```

这样无论脚本在 `tools/`、`scripts/` 还是根目录运行，路径都能正确解析。

---

## 🔒 .gitignore 相关

- `logs/` — 已全局忽略，无需额外添加
- `tmp/` — 已全局忽略，无需额外添加
- `tools/` 中的特定临时脚本 — 已在 `.gitignore` 中配置

---

## 🎯 特殊说明

- `scripts/` vs `tools/` 的区别：
  - `scripts/`：项目生命周期内长期使用的系统脚本（打包、验证、部署）
  - `tools/`：针对特定问题的一次性分析、诊断、数据迁移脚本，用完后可归档或删除
