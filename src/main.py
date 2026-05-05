"""
高低压成套设备招投标监控系统 - 主程序入口
"""
import os
import sys
import argparse
import logging
from datetime import datetime

# 添加src目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.storage import Storage, BidInfo
from crawler.registry import get_all_crawlers
from matcher.keyword import KeywordMatcher
from notifier.email import EmailNotifier
from scheduler.runner import Scheduler
from config.loader import load_config as _load_config
from config.schema import AppConfig


def load_config(config_path: str) -> AppConfig:
    """加载配置文件（统一入口）"""
    return _load_config(path=config_path, fill_defaults=True)


def setup_logging(config: AppConfig):
    """配置日志"""
    level = getattr(logging, config.logging.level.upper())
    log_file = config.logging.file
    
    handlers = [logging.StreamHandler()]
    
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


class BidMonitor:
    """招标监控器主类"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = logging.getLogger("monitor")
        
        # 初始化组件
        self.storage = Storage()
        self.matcher = KeywordMatcher(
            include_keywords=config.industry.include,
            exclude_keywords=config.industry.exclude,
            must_contain_keywords=config.industry.must_contain,
        )
        self.notifier = EmailNotifier(config.email.model_dump())
        
        # 初始化爬虫
        self.crawlers = []
        crawler_cfg = config.crawler
        enabled_sites = crawler_cfg.enabled_sites or ['ccgp', 'chinabidding', 'ebnew']
        
        crawler_classes = get_all_crawlers()
        for site in enabled_sites:
            if site in crawler_classes:
                crawler_class = crawler_classes[site]
                crawler = crawler_class({
                    **crawler_cfg.model_dump(),
                    'search_keywords': config.industry.include[:3]  # 使用前3个关键字搜索
                })
                self.crawlers.append(crawler)
                self.logger.info(f"已启用爬虫: {site}")
    
    def run_once(self):
        """执行一次监控任务"""
        self.logger.info("=" * 50)
        self.logger.info(f"开始监控任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_matched_bids = []
        
        # 遍历所有爬虫
        for crawler in self.crawlers:
            try:
                self.logger.info(f"正在爬取: {crawler.name}")
                bids = crawler.crawl()
                
                if bids is None:
                    self.logger.warning(f"爬虫 {crawler.name} 返回空结果，可能请求失败")
                    continue
                
                # 匹配关键字
                for bid in bids:
                    match_result = self.matcher.match_any(bid.title, bid.content)
                    
                    if match_result.matched:
                        # 检查是否已存在
                        if not self.storage.exists(bid):
                            self.storage.save(bid, notified=False)
                            all_matched_bids.append(bid)
                            self.logger.info(f"[新] 匹配招标: {bid.title[:50]}... 关键字: {match_result.matched_keywords}")
                    elif match_result.excluded_by:
                        self.logger.debug(f"排除: {bid.title[:30]}... (包含排除词: {match_result.excluded_by})")
                        
            except Exception as e:
                self.logger.error(f"爬虫 {crawler.name} 执行失败: {e}")
        
        # 发送通知
        if all_matched_bids:
            self.logger.info(f"发现 {len(all_matched_bids)} 条新招标信息，准备发送通知...")
            success = self.notifier.send(all_matched_bids)
            
            if success:
                # 标记为已通知
                for bid in all_matched_bids:
                    self.storage.mark_notified(bid)
                self.logger.info("邮件发送成功")
            else:
                self.logger.error("邮件发送失败，下次将重新发送")
        else:
            self.logger.info("本次检查没有发现新的匹配招标信息")
        
        self.logger.info(f"监控任务完成 - 数据库共 {self.storage.count_all()} 条记录")
        self.logger.info("=" * 50)
    
    def test_email(self):
        """测试邮件发送"""
        self.logger.info("发送测试邮件...")
        success = self.notifier.send_test()
        if success:
            self.logger.info("测试邮件发送成功，请检查收件箱")
        else:
            self.logger.error("测试邮件发送失败，请检查邮件配置")
        return success


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='高低压成套设备招投标监控系统')
    parser.add_argument('--config', '-c', default='config/config.yaml',
                        help='Config file path (default: config/config.yaml)')
    parser.add_argument('--crawl-once', action='store_true',
                        help='Crawl once without starting scheduler')
    parser.add_argument('--test-email', action='store_true',
                        help='Send a test email')
    
    args = parser.parse_args()
    
    # 切换到脚本所在目录
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 加载配置
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"错误: 配置文件不存在 - {args.config}")
        print("请复制 config/config.yaml.example 并配置您的邮箱信息")
        sys.exit(1)
    
    # 配置日志
    setup_logging(config)
    logger = logging.getLogger("main")
    
    logger.info("=" * 60)
    logger.info("  高低压成套设备招投标监控系统 启动")
    logger.info("=" * 60)
    
    # 创建监控器
    monitor = BidMonitor(config)
    
    # 根据参数执行不同操作
    if args.test_email:
        monitor.test_email()
    elif args.crawl_once:
        monitor.run_once()
    else:
        # 启动定时任务
        scheduler = Scheduler(
            interval_minutes=config.schedule.interval_minutes,
            run_immediately=config.schedule.run_immediately
        )
        
        logger.info(f"启动定时监控，间隔 {config.schedule.interval_minutes} 分钟")
        logger.info("按 Ctrl+C 停止程序")
        
        scheduler.start(monitor.run_once)


if __name__ == '__main__':
    main()
