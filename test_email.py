#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件发送模块
负责将股票分析报告以HTML格式发送至指定邮箱
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import logging
import os
import re
from datetime import datetime
from config import Config

# 初始化日志
logger = logging.getLogger(__name__)

def is_valid_email(email: str) -> bool:
    """验证邮箱格式是否正确"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

def send_stock_analysis_report(stock_code: str, report: str) -> bool:
    """
    发送股票分析报告邮件
    
    Args:
        stock_code: 股票代码
        report: 分析报告内容
    
    Returns:
        bool: 是否成功发送
    """
    try:
        # 获取当前北京时间
        beijing_now = datetime.now(Config.BEIJING_TIMEZONE)
        
        # 验证邮箱格式
        if not is_valid_email(Config.MAIL_USERNAME):
            logger.error(f"发件人邮箱格式无效: {Config.MAIL_USERNAME}")
            return False
            
        if not is_valid_email(Config.MAIL_TO):
            logger.error(f"收件人邮箱格式无效: {Config.MAIL_TO}")
            return False
            
        # 邮件主题
        subject = f"{stock_code} 股票分析报告 - {beijing_now.strftime('%Y-%m-%d')}"
        
        # 邮件内容
        html_content = generate_html_report(stock_code, report, beijing_now)
        
        # 创建邮件对象
        msg = MIMEMultipart()
        msg['From'] = f"{Config.MAIL_SENDER_NAME} <{Config.MAIL_USERNAME}>"
        msg['To'] = Config.MAIL_TO
        msg['Subject'] = Header(subject, 'utf-8')
        
        # 添加基础头信息（防止被标记为垃圾邮件）
        msg['Message-ID'] = f"<{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{os.getpid()}@{Config.MAIL_USERNAME.split('@')[1]}>"
        msg['Date'] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
        msg['X-Mailer'] = "Python SMTP"
        msg['X-Priority'] = '1'
        msg['X-MSMail-Priority'] = 'High'
        msg['Importance'] = 'High'
        
        # 为临时邮箱服务添加特殊头信息
        temp_mail_domains = ['temp-mail.org', '10minutemail.com', 'mailinator.com', 
                             'guerrillamail.com', 'yopmail.com', 'throwawaymail.com']
        if any(domain in Config.MAIL_TO.lower() for domain in temp_mail_domains):
            logger.info("检测到临时邮箱服务，添加特殊头信息")
            msg['List-Unsubscribe'] = f"<mailto:{Config.MAIL_USERNAME}?subject=unsubscribe>"
            msg['X-Complaints-To'] = Config.MAIL_USERNAME
            msg['Precedence'] = 'bulk'
        
        # 添加HTML内容
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        # 详细日志记录
        logger.info(f"准备发送邮件:")
        logger.info(f"  邮件服务器: {Config.MAIL_SERVER}:{Config.MAIL_PORT}")
        logger.info(f"  发件人: {Config.MAIL_USERNAME}")
        logger.info(f"  收件人: {Config.MAIL_TO}")
        logger.info(f"  主题: {subject}")
        logger.info(f"  邮件大小: {len(html_content)} 字节")
        
        # 发送邮件
        try:
            # 创建SSL上下文
            context = ssl.create_default_context()
            
            # 连接到邮件服务器
            with smtplib.SMTP_SSL(Config.MAIL_SERVER, Config.MAIL_PORT, context=context) as server:
                # 登录
                server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
                logger.info("SMTP登录成功")
                
                # 发送邮件
                server.sendmail(Config.MAIL_USERNAME, Config.MAIL_TO.split(','), msg.as_string())
                logger.info(f"股票分析报告邮件已成功发送至 {Config.MAIL_TO}")
                
                # 添加额外延迟，确保邮件被完全发送
                import time
                time.sleep(1)
                
                return True
            
        except smtplib.SMTPAuthenticationError as auth_err:
            logger.error(f"SMTP认证失败: {str(auth_err)}")
            logger.error("请检查: 1. 邮箱授权码是否正确 2. 是否开启了SMTP服务")
            return False
            
        except Exception as e:
            logger.error(f"邮件发送过程中发生未知错误: {str(e)}")
            return False
    
    except Exception as e:
        error_msg = f"发送股票分析报告邮件失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False

def generate_html_report(stock_code: str, report: str, report_time: datetime) -> str:
    """
    生成HTML格式的报告
    
    Args:
        stock_code: 股票代码
        report: 纯文本报告
        report_time: 报告生成时间
    
    Returns:
        str: HTML格式的报告
    """
    try:
        # 分割报告为段落
        paragraphs = report.split('\n\n')
        
        # 构建HTML内容
        html = """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>股票分析报告</title>
            <style>
                body {
                    font-family: 'Microsoft YaHei', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 900px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .report-container {
                    background-color: #fff;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    padding: 30px;
                }
                h1 {
                    color: #2c3e50;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }
                h2 {
                    color: #2980b9;
                    margin-top: 25px;
                    border-left: 4px solid #3498db;
                    padding-left: 10px;
                }
                h3 {
                    color: #16a085;
                    margin-top: 20px;
                }
                p {
                    margin: 15px 0;
                }
                .section {
                    margin-bottom: 25px;
                }
                .highlight {
                    background-color: #f8f9fa;
                    border-left: 3px solid #3498db;
                    padding: 15px;
                    border-radius: 0 4px 4px 0;
                }
                .conclusion {
                    background-color: #e8f4fc;
                    padding: 20px;
                    border-radius: 8px;
                    border: 1px solid #3498db;
                }
                .key-points {
                    background-color: #f9f9f9;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 15px 0;
                }
                .footer {
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #7f8c8d;
                    font-size: 0.9em;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }
                table, th, td {
                    border: 1px solid #ddd;
                }
                th {
                    background-color: #f2f2f2;
                    padding: 10px;
                    text-align: left;
                }
                td {
                    padding: 8px 10px;
                }
                tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
                .positive {
                    color: #27ae60;
                    font-weight: bold;
                }
                .negative {
                    color: #e74c3c;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="report-container">
                <h1>股票分析报告</h1>
                <div class="report-header">
                    <p><strong>股票代码：</strong> {stock_code}</p>
                    <p><strong>报告时间：</strong> {report_time}</p>
                </div>
                
                <div class="report-content">
        """
        
        # 处理报告内容，转换为HTML
        for i, paragraph in enumerate(paragraphs):
            if not paragraph.strip():
                continue
                
            lines = paragraph.split('\n')
            
            # 标题处理
            if i == 0:  # 第一段是标题
                html += f"<h1>{lines[0]}</h1>"
                if len(lines) > 1:
                    html += "<div class='section'>"
                    for line in lines[1:]:
                        if line.strip():
                            html += f"<p>{line}</p>"
                    html += "</div>"
                continue
            
            # 一级标题（以数字加"、"开头）
            if lines[0].endswith('、') and lines[0][0].isdigit():
                html += f"<h2>{lines[0]}</h2>"
                html += "<div class='section'>"
                for line in lines[1:]:
                    if line.strip():
                        # 表格处理
                        if '\t' in line:
                            html += "<table>"
                            # 表头
                            headers = line.split('\t')
                            html += "<tr>"
                            for header in headers:
                                html += f"<th>{header}</th>"
                            html += "</tr>"
                            html += "</table>"
                        else:
                            html += f"<p>{line}</p>"
                html += "</div>"
                continue
            
            # 二级标题（以数字加"．"开头）
            if lines[0].endswith('．') and lines[0][0].isdigit():
                html += f"<h3>{lines[0]}</h3>"
                html += "<div class='section'>"
                for line in lines[1:]:
                    if line.strip():
                        html += f"<p>{line}</p>"
                html += "</div>"
                continue
            
            # 普通段落
            html += "<div class='section'>"
            for line in lines:
                if line.startswith('•'):
                    html += f"<p style='margin-left: 20px;'>{line}</p>"
                elif line.strip():
                    html += f"<p>{line}</p>"
            html += "</div>"
        
        # 添加结论部分样式
        html = html.replace("当前综合评分为", "<div class='conclusion'><strong>当前综合评分为")
        html = html.replace("风险提示：", "</strong></div><div class='key-points'><strong>风险提示：</strong>")
        html = html.replace("(注：", "</div><p style='font-style: italic;'>(注：")
        
        # 完成HTML
        html += """
                </div>
                
                <div class="footer">
                    <p>本报告由Stock Analyse系统自动生成，仅供参考，不构成投资建议。</p>
                    <p>数据来源：AkShare、新浪财经等公开数据源</p>
                    <p>免责声明：市场有风险，投资需谨慎。</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 替换占位符
        html = html.replace("{stock_code}", stock_code)
        html = html.replace("{report_time}", report_time.strftime("%Y年%m月%d日 %H:%M"))
        
        return html
    
    except Exception as e:
        error_msg = f"生成HTML报告失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return f"<html><body><h1>报告生成错误</h1><p>{error_msg}</p></body></html>"

def test_email_connection() -> bool:
    """
    测试邮件服务器连接
    
    Returns:
        bool: 连接是否成功
    """
    try:
        logger.info(f"测试邮件服务器连接: {Config.MAIL_SERVER}:{Config.MAIL_PORT}")
        
        # 创建SSL上下文
        context = ssl.create_default_context()
        
        # 连接到邮件服务器
        with smtplib.SMTP_SSL(Config.MAIL_SERVER, Config.MAIL_PORT, context=context) as server:
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        
        logger.info("邮件服务器连接测试成功")
        return True
    except smtplib.SMTPAuthenticationError as auth_err:
        logger.error(f"SMTP认证失败: {str(auth_err)}")
        logger.error("请检查: 1. 邮箱授权码是否正确 2. 是否开启了SMTP服务")
        return False
    except Exception as e:
        error_msg = f"邮件服务器连接测试失败: {str(e)}"
        logger.error(error_msg)
        return False

# 模块初始化
try:
    logger.info("邮件发送模块初始化完成")
    
    # 测试邮件服务器连接（仅在调试模式下）
    if os.getenv("DEBUG", "").lower() in ("true", "1", "yes"):
        logger.info("调试模式启用，测试邮件服务器连接")
        if test_email_connection():
            logger.info("邮件服务器连接测试成功")
        else:
            logger.warning("邮件服务器连接测试失败")
    
except Exception as e:
    logger.error(f"邮件发送模块初始化失败: {str(e)}", exc_info=True)
