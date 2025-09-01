#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置模块
提供项目全局配置参数，包括路径、日志、邮件配置等
"""

import os
import logging
import sys
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta

# 获取项目根目录路径
def _get_base_dir() -> str:
    """获取项目根目录路径"""
    try:
        # 优先使用GITHUB_WORKSPACE环境变量（GitHub Actions环境）
        base_dir = os.environ.get('GITHUB_WORKSPACE')
        if base_dir and os.path.exists(base_dir):
            return os.path.abspath(base_dir)
        
        # 尝试基于当前文件位置计算项目根目录
        current_file_path = os.path.abspath(__file__)
        base_dir = os.path.dirname(os.path.dirname(current_file_path))
        
        # 确保目录存在
        if os.path.exists(base_dir):
            return os.path.abspath(base_dir)
        
        # 作为最后手段，使用当前工作目录
        return os.path.abspath(os.getcwd())
    except Exception as e:
        print(f"获取项目根目录失败: {str(e)}", file=sys.stderr)
        # 退回到当前工作目录
        return os.path.abspath(os.getcwd())

class Config:
    """
    全局配置类：数据源配置、策略参数、文件路径管理
    所有配置项均有默认值，并支持从环境变量覆盖
    """
    
    # -------------------------
    # 0. 时区定义
    # -------------------------
    # 严格遵守要求：在config.py中定义两个变量，分别保存平台时间UTC，北京时间UTC+8
    UTC_TIMEZONE = timezone.utc
    BEIJING_TIMEZONE = timezone(timedelta(hours=8))
    
    # -------------------------
    # 1. 文件路径配置 - 基于仓库根目录的路径
    # -------------------------
    BASE_DIR: str = _get_base_dir()
    
    # 数据存储路径
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    
    # 日志配置
    LOG_DIR: str = os.path.join(DATA_DIR, "logs")  # 日志目录配置
    LOG_FILE: str = os.path.join(LOG_DIR, "stock_analyse.log")  # 日志文件路径
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # -------------------------
    # 2. 邮件配置
    # -------------------------
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.qq.com")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", "465"))
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_SENDER_NAME: str = os.getenv("MAIL_SENDER_NAME", "Stock Analyse系统")
    MAIL_TO: str = os.getenv("MAIL_TO", "recipient@example.com")
    
    # -------------------------
    # 3. 数据源配置
    # -------------------------
    # 初次爬取默认时间范围（1年）
    INITIAL_CRAWL_DAYS: int = 365
    
    # 股票列表更新间隔（天）
    STOCK_LIST_UPDATE_INTERVAL: int = 7
    
    # 英文列名到中文列名的映射
    COLUMN_NAME_MAPPING: Dict[str, str] = {
        "date": "日期",
        "open": "开盘",
        "close": "收盘",
        "high": "最高",
        "low": "最低",
        "volume": "成交量",
        "amount": "成交额",
        "amplitude": "振幅",
        "pct_change": "涨跌幅",
        "price_change": "涨跌额",
        "turnover": "换手率",
        "stock_code": "股票代码",
        "stock_name": "股票名称",
        "industry": "行业",
        "area": "地域",
        "listing_date": "上市日期"
    }
    
    # 标准列名（中文）
    STANDARD_COLUMNS: list = list(COLUMN_NAME_MAPPING.values())
    
    # 股票列表标准列
    STOCK_STANDARD_COLUMNS: list = ["股票代码", "股票名称", "行业", "地域", "上市日期"]
    
    # -------------------------
    # 4. 路径初始化方法
    # -------------------------
    @staticmethod
    def init_dirs() -> bool:
        """
        初始化所有必要目录
        :return: 是否成功初始化所有目录
        """
        try:
            # 确保数据目录存在
            dirs_to_create = [
                Config.DATA_DIR,
                Config.LOG_DIR
            ]
            
            for dir_path in dirs_to_create:
                if dir_path and not os.path.exists(dir_path):
                    os.makedirs(dir_path, exist_ok=True)
                    logging.info(f"创建目录: {dir_path}")
            
            # 初始化日志
            Config.setup_logging(log_file=Config.LOG_FILE)
            
            return True
            
        except Exception as e:
            logging.error(f"初始化目录失败: {str(e)}", exc_info=True)
            return False
    
    # -------------------------
    # 5. 日志配置
    # -------------------------
    @staticmethod
    def setup_logging(log_level: Optional[str] = None,
                     log_file: Optional[str] = None) -> None:
        """
        配置日志系统
        :param log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        :param log_file: 日志文件路径，如果为None则只输出到控制台
        """
        try:
            level = log_level or Config.LOG_LEVEL
            log_format = Config.LOG_FORMAT
            
            # 创建根日志记录器
            root_logger = logging.getLogger()
            root_logger.setLevel(level)
            
            # 清除现有处理器
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            
            # 创建格式化器
            formatter = logging.Formatter(log_format)
            
            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
            
            # 创建文件处理器（如果指定了日志文件）
            if log_file:
                try:
                    # 确保日志目录存在
                    log_dir = os.path.dirname(log_file)
                    if log_dir and not os.path.exists(log_dir):
                        os.makedirs(log_dir, exist_ok=True)
                    
                    file_handler = logging.FileHandler(log_file, encoding='utf-8')
                    file_handler.setLevel(level)
                    file_handler.setFormatter(formatter)
                    root_logger.addHandler(file_handler)
                    logging.info(f"日志文件已配置: {log_file}")
                except Exception as e:
                    logging.error(f"配置日志文件失败: {str(e)}", exc_info=True)
        except Exception as e:
            logging.error(f"配置日志系统失败: {str(e)}", exc_info=True)

# -------------------------
# 初始化配置
# -------------------------
try:
    # 首先尝试初始化基础目录
    base_dir = _get_base_dir()
    
    # 重新定义关键路径，确保它们基于正确的base_dir
    Config.BASE_DIR = base_dir
    Config.DATA_DIR = os.path.join(base_dir, "data")
    Config.LOG_DIR = os.path.join(Config.DATA_DIR, "logs")
    Config.LOG_FILE = os.path.join(Config.LOG_DIR, "stock_analyse.log")
    
    # 设置基础日志配置
    logging.basicConfig(
        level=Config.LOG_LEVEL,
        format=Config.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 初始化目录
    if Config.init_dirs():
        logging.info("配置初始化完成")
    else:
        logging.warning("配置初始化完成，但存在警告")
        
except Exception as e:
    # 创建一个临时的、基本的日志配置
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 记录错误但继续执行
    logging.error(f"配置初始化失败: {str(e)}", exc_info=True)
    logging.info("已设置基础日志配置，继续执行")

# -------------------------
# 检查环境变量
# -------------------------
try:
    mail_server = os.getenv("MAIL_SERVER")
    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")
    
    if mail_server and mail_username and mail_password:
        logging.info("检测到邮件服务器配置已设置")
    else:
        logging.warning("邮件服务器配置不完整，邮件发送功能将不可用")
        
except Exception as e:
    logging.error(f"检查环境变量时出错: {str(e)}", exc_info=True)