# 🔍 BidMonitor AI - 高低压成套设备招标智能监控系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 📖 项目简介

**BidMonitor AI** 是一款专为**高低压成套设备行业**深度定制的智能招投标监控系统。

不同于通用招标监控工具，本项目针对行业特性进行了全方位优化：内置高压开关柜（KYN28、HXGN）、低压配电柜（GGD/GCK/GCS/MNS）、箱式变电站、环网柜、开闭所、电容补偿柜等产品词库，AI 筛选提示词围绕行业业务边界精准设计，确保不错过任何一个配电设备采购商机。

### 核心能力

- 🏭 **行业深度定制** - 专为高低压成套设备行业打造，产品词库 + AI 业务边界定义
- 🌐 **多源招标监控** - 覆盖政府采购网、电网公司、发电集团、电力行业平台、工程总包 5 大类信息源
- 🤖 **AI 智能过滤** - 支持 50+ AI Provider（DeepSeek、OpenAI、Kimi、通义千问等），一键测速、智能切换
- 🛡️ **网站健康检测** - 实时监控各招标网站可用性，自动标记异常源
- 📧 **多渠道通知** - 邮件、短信、微信、语音电话，支持多联系人管理
- 🖥️ **双端部署** - Windows 桌面 GUI 版 + 服务器 Web 版（FastAPI）
- 🔧 **规则引擎** - 自定义网站配置，CSS Selector + Selenium 动态渲染
- 🔐 **敏感配置分离** - API Key、密码等敏感信息独立存放 `.env`，安全不泄露

---

## 🏭 行业定制架构

本项目采用**行业定义层**设计，所有行业相关配置集中在 `src/domain/` 目录下：

| 文件 | 作用 |
|------|------|
| `src/domain/industry.py` | 行业名称、产品词库、默认关键词、排除词 |
| `src/domain/sites.py` | 监控网站列表（按行业特点精选 5 大类） |
| `src/domain/prompts.py` | AI 筛选的系统提示词，定义业务边界 |

### 产品词库覆盖

- **高压设备**：KYN28、HXGN、中置柜、环网柜、高压配电柜
- **低压设备**：GGD、GCK、GCS、MNS、抽屉柜、固定式开关柜
- **箱变/配电**：箱式变电站、预装式变电站、配电箱、动力箱、JP柜
- **成套系统**：高低压成套设备、成套开关设备、开关柜、配电屏
- **专用柜体**：电容补偿柜、有源滤波柜、动力柜、控制柜、变频柜、母线槽
- **电力配套**：开闭所、开关站、配电房、变电站、升压站

### 智能排除

默认排除非设备采购类信息：设计、监理、咨询、清洗、运输、弱电、安防、消防、智能化、仅施工、劳务分包。

---

## 🚀 快速开始

### 环境准备

```bash
# 克隆仓库
git clone https://github.com/goaltang/BidMonitor-AI-Webhook.git
cd BidMonitor-AI-Webhook

# 创建虚拟环境（推荐）
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置敏感信息

```bash
cp .env.example .env
# 编辑 .env，填写 API Key、邮箱密码等敏感信息
```

### 运行桌面版

```bash
python run.py
```

### 运行服务器版

```bash
cd server
pip install -r requirements.txt
python app.py
# 访问 http://localhost:8080
# 默认账号: CDKJ / 密码: cdkj
```

详细部署请参考 [`server/DEPLOY.md`](server/DEPLOY.md)

---

## ✨ 核心特性详解

### 1. 网站源配置重构

`src/domain/sites.py` 作为**单一事实来源（SSOT）**，统一管理所有监控网站：

- **5 大分类体系**：通用招标平台、电网公司、电力行业平台、发电集团、工程总包
- **独立网站配置**：每个网站可单独设置超时、重试次数、请求间隔、请求头、Selenium 开关
- **规则引擎**：自定义网站支持 CSS Selector 解析、翻页模板、最大页数限制
- **健康检测**：`SiteHealthChecker` 并发探测，三级状态（🟢 正常 / 🟡 缓慢 / 🔴 宕机），HEAD 请求优先，405 自动回退 GET

### 2. AI 多 Provider 管理模式

`src/ai_providers.py` 内置 **50+ Provider 预设**：

- **国际官方**：OpenAI、Claude、Gemini、DeepSeek、Groq、Mistral、Cohere、xAI
- **国产官方**：Kimi、智谱 GLM、通义千问、讯飞星火、文心一言、豆包、百川、MiniMax、零一万物、阶跃星辰、腾讯混元、商汤商量
- **中转聚合**：OpenRouter、API2D、OhMyGPT、APIYI、CloseAI、OneAPI 等
- **国内云**：阿里云百炼、腾讯云 TI、百度千帆、火山引擎、硅基流动
- **企业云**：Azure OpenAI、AWS Bedrock、NVIDIA NIM、Together AI

功能特性：
- 一键从预设创建 / 完全自定义 Provider
- **实时测速**：使用极简 Prompt 测试连接延迟
- **请求格式自动适配**：OpenAI、Anthropic、Gemini、Cohere、MiniMax、Bedrock 等
- **响应统一解析**：自动处理各种返回格式
- GUI 中带状态图标和延迟显示：`🟢 DeepSeek 120ms`

### 3. 敏感配置分离

安全机制：
- `config/config.yaml` 只存放非敏感字段（SMTP 服务器、端口等）
- `.env` 存放 API Key、SMTP 密码、短信/语音 AccessKey Secret
- `.env` 被 Git 忽略，运行时通过 `python-dotenv` 加载
- 服务端保存配置时，敏感字段（`api_key`、`password`、`access_key_secret`）受保护：前端传空 / `***` 时不覆盖原值

### 4. 爬虫架构

- **注册表模式**：`@register_crawler('ccgp')` 装饰器自动注册，统一管理
- **爬虫基类**：User-Agent 池、完整请求头模拟、指数退避重试（2, 4, 8... 秒 + 随机抖动）、SSL 跳过、反爬虫检测
- **专用爬虫**：中国政府采购网、中国采购与招标网、必联网、军队采购网、电力招标网 等
- **通用爬虫**：`CustomCrawler`（规则引擎）、`SeleniumCrawler`（动态渲染）
- **共享浏览器管理器**：`SharedBrowserManager` 统一调度 Selenium 实例，任务结束后释放内存

### 5. 通知方式

| 方式 | 服务商 | 特点 |
|------|--------|------|
| 📧 邮件 | SMTP（QQ/163/阿里/Gmail/Outlook/企业邮箱） | 支持多邮箱账户同时发送 |
| 📱 短信 | 阿里云、腾讯云 | 签名 + 模板 CODE 配置 |
| 💬 微信 | PushPlus、企业微信 Webhook | Token / Webhook URL |
| 📞 语音 | 阿里云语音服务 | TTS 模板、被叫显号 |

联系人系统支持按人启用/禁用，遍历发送。

---

## 📁 项目结构

```
BidMonitor-AI-Webhook/
├── src/                          # 核心源码
│   ├── domain/                   # 行业定义层
│   │   ├── industry.py           # 高低压成套设备行业词库与默认配置
│   │   ├── sites.py              # 网站源单一事实来源（分类/配置）
│   │   └── prompts.py            # AI 筛选系统提示词
│   ├── crawler/                  # 爬虫模块
│   │   ├── base.py               # 爬虫基类（重试/UA池/反爬检测）
│   │   ├── registry.py           # 爬虫注册表
│   │   ├── health.py             # 网站健康检测
│   │   ├── builtin/              # 内置专用爬虫
│   │   ├── custom.py             # 通用自定义爬虫（规则引擎）
│   │   └── selenium_crawler.py   # Selenium 动态渲染爬虫
│   ├── matcher/                  # 匹配引擎
│   ├── notifier/                 # 通知模块
│   │   ├── email.py              # 邮件通知
│   │   ├── sms.py                # 短信通知
│   │   ├── wechat.py             # 微信推送
│   │   └── voice.py              # 语音电话
│   ├── database/                 # 数据存储（SQLite）
│   ├── scheduler/                # 定时调度
│   ├── config/                   # 配置管理
│   ├── gui.py                    # Tkinter 桌面 GUI
│   ├── monitor_core.py           # 监控调度核心
│   └── ai_providers.py           # AI Provider 管理（50+预设）
├── server/                       # 服务器 Web 版
│   ├── app.py                    # FastAPI 主应用 + API
│   ├── static/index.html         # Web 前端（单页应用）
│   ├── setup.sh                  # 一键部署脚本
│   ├── start.sh / stop.sh        # 启停脚本
│   ├── bidmonitor.service        # systemd 服务配置
│   └── DEPLOY.md                 # 部署指南
├── config/
│   └── config.yaml               # 系统默认配置（非敏感）
├── data/
│   └── bids.db                   # SQLite 数据库
├── scripts/
│   ├── analyze_cpeinet.py        # 网站分析工具
│   ├── verify_system.py          # 系统验证
│   └── pack.bat                  # Windows 打包脚本
├── tools/                        # 分析/诊断/一次性工具脚本
├── logs/                         # 运行日志与输出文件
├── tmp/                          # 临时抓取的 HTML/数据
├── docs/                         # 规划文档、迁移指南
├── run.py                        # 桌面版入口
├── .env.example                  # 敏感配置模板
├── requirements.txt              # 依赖列表
└── README.md                     # 本文档
```

---

## 🔧 配置指南

首次运行后，在 GUI 或 Web 界面中配置：

1. **关键词** - 系统已预置行业默认关键词，可按需调整
2. **网站源** - 按 5 大分类勾选需要监控的招标网站，查看健康状态
3. **AI 过滤** - 选择 Provider、配置 API Key、测试连接
4. **通知方式** - 配置邮箱 / 短信 / 微信 / 语音
5. **联系人** - 添加接收通知的人员信息

配置文件说明：

| 文件 | 用途 | 是否入 Git |
|------|------|-----------|
| `src/domain/industry.py` | 行业词库、默认关键词、排除词 | ✅ |
| `config/config.yaml` | 系统默认配置、爬虫全局参数 | ✅ |
| `.env` | API Key、SMTP 密码、AccessKey Secret | ❌（已忽略） |
| `user_config.json` | 用户 GUI 配置（主题、Provider、启用网站等） | ❌（已忽略） |
| `server/server_config.json` | Web 版独立配置 | ❌（已忽略） |

---

## 🔄 切换行业

如需适配其他行业（如变压器、电线电缆、电力施工等），只需：

1. 新建行业文件（如 `src/domain/industry_transformer.py`）
2. 修改产品词库 `PRODUCT_KEYWORDS`、默认关键词、排除词
3. 调整 `src/domain/sites.py` 中的网站列表（按需增删）
4. 更新 `src/domain/prompts.py` 中的 AI 业务边界描述

无需改动爬虫、通知、GUI 等核心模块。

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

⭐ 如果这个项目对你有帮助，请给个 Star！
