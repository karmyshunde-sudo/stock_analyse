#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析系统
接收股票代码，进行详细分析并发送邮件报告
"""

import os
import sys
import json
import logging
import traceback
import argparse
from datetime import datetime
from typing import Dict, Any, Optional
from config import Config
from stock_scoring import analyze_stock
from email_sender import send_stock_analysis_report

# 初始化日志
Config.setup_logging(log_file=Config.LOG_FILE)
logger = logging.getLogger(__name__)

def main(stock_code: str) -> Dict[str, Any]:
    """
    主函数：执行股票分析流程
    
    Args:
        stock_code: 股票代码
    
    Returns:
        Dict[str, Any]: 任务执行结果
    """
    try:
        # 获取当前时间
        beijing_now = datetime.now(Config.BEIJING_TIMEZONE)
        logger.info(f"===== 开始执行股票分析任务：{stock_code} =====")
        logger.info(f"北京时间：{beijing_now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 设置环境
        if not setup_environment():
            error_msg = "环境设置失败，任务终止"
            logger.error(error_msg)
            return {"status": "error", "stock_code": stock_code, "message": error_msg}
        
        # 执行股票分析
        logger.info(f"开始分析股票：{stock_code}")
        analysis_result = analyze_stock(stock_code)
        
        # 检查分析结果
        if analysis_result["status"] != "success":
            error_msg = f"股票分析失败: {analysis_result.get('message', '未知错误')}"
            logger.error(error_msg)
            return {"status": "error", "stock_code": stock_code, "message": error_msg}
        
        # 生成并发送邮件报告
        report = analysis_result["report"]
        logger.info("生成股票分析报告")
        send_success = send_stock_analysis_report(stock_code, report)
        
        if send_success:
            logger.info("股票分析报告邮件发送成功")
            return {
                "status": "success",
                "stock_code": stock_code,
                "message": "股票分析报告已发送至指定邮箱",
                "report_date": beijing_now.strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            error_msg = "股票分析报告邮件发送失败"
            logger.error(error_msg)
            return {"status": "failed", "stock_code": stock_code, "message": error_msg}
    
    except Exception as e:
        error_msg = f"主程序执行失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "status": "error",
            "stock_code": stock_code,
            "message": error_msg,
            "timestamp": datetime.now(Config.BEIJING_TIMEZONE).isoformat()
        }

def setup_environment() -> bool:
    """
    设置运行环境，检查必要的目录和文件
    
    Returns:
        bool: 环境设置是否成功
    """
    try:
        # 获取当前时间
        beijing_now = datetime.now(Config.BEIJING_TIMEZONE)
        
        logger.info(f"开始设置运行环境 (CST: {beijing_now})")
        
        # 确保必要的目录存在
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        os.makedirs(Config.LOG_DIR, exist_ok=True)
        
        # 检查邮箱配置
        if not Config.MAIL_SERVER or not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
            logger.warning("邮件服务器配置不完整，邮件发送将不可用")
            return False
        
        # 记录环境信息
        logger.info(f"当前北京时间: {beijing_now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        logger.info("环境设置完成")
        return True
    except Exception as e:
        error_msg = f"环境设置失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='股票分析系统')
    parser.add_argument('stock_code', type=str, help='要分析的股票代码（例如：002511.SZ）')
    args = parser.parse_args()
    
    # 执行主程序
    result = main(args.stock_code)
    
    # 输出JSON格式的结果
    print(json.dumps(result, indent=2, ensure_ascii=False))