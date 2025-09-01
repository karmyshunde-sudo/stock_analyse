#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析模块
负责对股票数据进行综合评分和分析，生成详细报告
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
from config import Config
from stock_crawler import (
    get_stock_basic_info,
    get_stock_daily_data,
    get_stock_realtime_data,
    get_technical_indicators,
    get_fund_flow_data,
    get_financial_data,
    get_stock_news,
    get_stock_index_data
)

# 初始化日志
logger = logging.getLogger(__name__)

def analyze_stock(stock_code: str) -> Dict[str, Any]:
    """
    分析股票并生成详细报告
    
    Args:
        stock_code: 股票代码
    
    Returns:
        Dict[str, Any]: 分析结果
    """
    try:
        logger.info(f"开始分析股票：{stock_code}")
        
        # 1. 获取基本数据
        basic_info = get_stock_basic_info(stock_code)
        if not basic_info:
            error_msg = f"无法获取股票 {stock_code} 基本信息，分析终止"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
        
        realtime_data = get_stock_realtime_data(stock_code)
        if not realtime_data:
            error_msg = f"无法获取股票 {stock_code} 实时数据，分析终止"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
        
        daily_data = get_stock_daily_data(stock_code)
        if daily_data.empty:
            error_msg = f"无法获取股票 {stock_code} 日线数据，分析终止"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
        
        # 2. 获取分析数据
        technical_indicators = get_technical_indicators(stock_code)
        fund_flow_data = get_fund_flow_data(stock_code)
        financial_data = get_financial_data(stock_code)
        news_data = get_stock_news(stock_code)
        
        # 3. 执行各项分析
        technical_analysis = analyze_technical_indicators(stock_code, technical_indicators, daily_data)
        fund_flow_analysis = analyze_fund_flow(stock_code, fund_flow_data)
        market_context_analysis = analyze_market_context(stock_code)
        financial_analysis = analyze_financial_data(stock_code, financial_data)
        news_analysis = analyze_news(stock_code, news_data)
        
        # 4. 生成综合报告
        report = generate_stock_analysis_report(
            stock_code,
            basic_info,
            realtime_data,
            technical_analysis,
            fund_flow_analysis,
            market_context_analysis,
            financial_analysis,
            news_analysis
        )
        
        logger.info(f"股票 {stock_code} 分析完成")
        return {
            "status": "success",
            "stock_code": stock_code,
            "report": report,
            "analysis_time": datetime.now(Config.BEIJING_TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        }
    
    except Exception as e:
        error_msg = f"分析股票 {stock_code} 时发生错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"status": "error", "message": error_msg}

def analyze_technical_indicators(stock_code: str, indicators: Dict[str, Any], daily_data: pd.DataFrame) -> Dict[str, Any]:
    """
    分析技术指标
    
    Args:
        stock_code: 股票代码
        indicators: 技术指标数据
        daily_data: 日线数据
    
    Returns:
        Dict[str, Any]: 技术分析结果
    """
    try:
        if not indicators:
            return {"status": "error", "message": "无技术指标数据"}
        
        current_price = daily_data['close'].iloc[-1] if not daily_data.empty else 0
        
        # 1. RSI分析
        rsi_14 = indicators.get('rsi_14', 50)
        rsi_status = "正常"
        rsi_comment = ""
        
        if rsi_14 > 70:
            rsi_status = "超买"
            rsi_comment = "RSI值高于70，显示短期上涨动能较强但需警惕回调风险"
        elif rsi_14 < 30:
            rsi_status = "超卖"
            rsi_comment = "RSI值低于30，显示短期下跌动能较强，可能有反弹机会"
        else:
            rsi_comment = "RSI值处于正常区间，市场情绪中性"
        
        # 2. 布林带分析
        boll_upper = indicators.get('boll_upper', 0)
        boll_middle = indicators.get('boll_middle', 0)
        boll_lower = indicators.get('boll_lower', 0)
        
        boll_status = "正常"
        boll_comment = ""
        
        if current_price > boll_upper:
            boll_status = "突破上轨"
            boll_comment = f"股价已突破布林带上轨({boll_upper:.2f})，显示短期强势，但可能面临回调压力"
        elif current_price < boll_lower:
            boll_status = "跌破下轨"
            boll_comment = f"股价已跌破布林带下轨({boll_lower:.2f})，显示短期弱势，但可能有反弹机会"
        else:
            boll_comment = "股价处于布林带通道内，波动率正常"
        
        # 3. 均线系统分析
        ma5 = indicators.get('ma5', 0)
        ma10 = indicators.get('ma10', 0)
        ma20 = indicators.get('ma20', 0)
        ma50 = indicators.get('ma50', 0)
        
        ma_status = "震荡"
        ma_comment = ""
        
        if ma5 > ma10 > ma20 > ma50:
            ma_status = "多头排列"
            ma_comment = "短期均线在长期均线上方，形成多头排列，中期趋势向好"
        elif ma5 < ma10 < ma20 < ma50:
            ma_status = "空头排列"
            ma_comment = "短期均线在长期均线下方，形成空头排列，中期趋势向弱"
        else:
            ma_comment = "均线系统处于震荡状态，无明显趋势"
        
        # 4. 支撑压力位分析
        resistance1 = indicators.get('resistance1', 0)
        support1 = indicators.get('support1', 0)
        recent_high = indicators.get('recent_high', 0)
        recent_low = indicators.get('recent_low', 0)
        
        # 5. MACD分析
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        macd_histogram = indicators.get('macd_histogram', 0)
        
        macd_status = "震荡"
        macd_comment = ""
        
        if macd > macd_signal and macd_histogram > 0:
            macd_status = "金叉"
            macd_comment = "MACD线在信号线上方，柱状体为正，显示上涨动能增强"
        elif macd < macd_signal and macd_histogram < 0:
            macd_status = "死叉"
            macd_comment = "MACD线在信号线下方，柱状体为负，显示下跌动能增强"
        else:
            macd_comment = "MACD处于震荡状态，无明显方向"
        
        # 6. 成交量分析
        volume_ma5 = indicators.get('volume_ma5', 0)
        volume_ma10 = indicators.get('volume_ma10', 0)
        volume_change = indicators.get('volume_change', 0)
        
        volume_status = "正常"
        volume_comment = ""
        
        if volume_change > 50:
            volume_status = "放量"
            volume_comment = f"成交量较5日均值增长{volume_change:.1f}%，显示市场活跃度提升"
        elif volume_change < -30:
            volume_status = "缩量"
            volume_comment = f"成交量较5日均值下降{abs(volume_change):.1f}%，显示市场活跃度降低"
        else:
            volume_comment = "成交量处于正常水平"
        
        # 7. 综合技术评分
        score = 50  # 基础分
        
        # RSI评分
        if 40 <= rsi_14 <= 60:
            score += 15
        elif 30 <= rsi_14 <= 70:
            score += 10
        else:
            score += 5
        
        # 布林带评分
        if current_price > boll_upper:
            score += 5  # 突破上轨可能有回调压力
        elif current_price < boll_lower:
            score += 15  # 跌破下轨可能有反弹机会
        else:
            score += 10  # 在通道内
        
        # 均线评分
        if ma_status == "多头排列":
            score += 20
        elif ma_status == "震荡":
            score += 10
        else:
            score += 5
        
        # MACD评分
        if macd_status == "金叉":
            score += 15
        elif macd_status == "震荡":
            score += 10
        else:
            score += 5
        
        # 成交量评分
        if volume_status == "放量":
            score += 10
        elif volume_status == "正常":
            score += 5
        else:
            score += 2
        
        # 限制评分在0-100之间
        score = max(0, min(100, score))
        
        return {
            "status": "success",
            "rsi_14": rsi_14,
            "rsi_status": rsi_status,
            "rsi_comment": rsi_comment,
            "boll_upper": boll_upper,
            "boll_middle": boll_middle,
            "boll_lower": boll_lower,
            "boll_status": boll_status,
            "boll_comment": boll_comment,
            "ma5": ma5,
            "ma10": ma10,
            "ma20": ma20,
            "ma50": ma50,
            "ma_status": ma_status,
            "ma_comment": ma_comment,
            "resistance1": resistance1,
            "support1": support1,
            "recent_high": recent_high,
            "recent_low": recent_low,
            "macd": macd,
            "macd_signal": macd_signal,
            "macd_histogram": macd_histogram,
            "macd_status": macd_status,
            "macd_comment": macd_comment,
            "volume_ma5": volume_ma5,
            "volume_ma10": volume_ma10,
            "volume_change": volume_change,
            "volume_status": volume_status,
            "volume_comment": volume_comment,
            "technical_score": score,
            "current_price": current_price
        }
    
    except Exception as e:
        error_msg = f"分析股票 {stock_code} 技术指标失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"status": "error", "message": error_msg}

def analyze_fund_flow(stock_code: str, fund_flow_data: pd.DataFrame) -> Dict[str, Any]:
    """
    分析资金流向
    
    Args:
        stock_code: 股票代码
        fund_flow_data: 资金流向数据
    
    Returns:
        Dict[str, Any]: 资金流向分析结果
    """
    try:
        if fund_flow_data.empty:
            return {"status": "warning", "message": "无资金流向数据"}
        
        # 获取最新资金流向数据
        latest_flow = fund_flow_data.iloc[-1]
        
        # 计算近期资金流向趋势
        recent_days = min(5, len(fund_flow_data))
        recent_flow = fund_flow_data.tail(recent_days)
        
        avg_main_net_inflow = recent_flow['main_net_inflow'].mean()
        avg_super_net_inflow = recent_flow['super_net_inflow'].mean()
        avg_large_net_inflow = recent_flow['large_net_inflow'].mean()
        
        # 分析主力资金流向
        main_net_inflow = latest_flow['main_net_inflow']
        main_flow_status = "净流入"
        main_flow_comment = ""
        
        if main_net_inflow > 0:
            main_flow_comment = f"主力资金净流入{main_net_inflow/1e4:.2f}万元，显示机构资金积极介入"
        else:
            main_flow_status = "净流出"
            main_flow_comment = f"主力资金净流出{abs(main_net_inflow)/1e4:.2f}万元，显示机构资金谨慎离场"
        
        # 分析超大单和大单流向
        super_net_inflow = latest_flow['super_net_inflow']
        large_net_inflow = latest_flow['large_net_inflow']
        
        institutional_flow_comment = ""
        if super_net_inflow > 0 and large_net_inflow > 0:
            institutional_flow_comment = "超大单和大单均呈现净流入，机构资金积极布局"
        elif super_net_inflow < 0 and large_net_inflow < 0:
            institutional_flow_comment = "超大单和大单均呈现净流出，机构资金谨慎离场"
        else:
            institutional_flow_comment = "超大单和大单流向不一致，机构资金存在分歧"
        
        # 分析中单和小单流向
        medium_net_inflow = latest_flow['medium_net_inflow']
        small_net_inflow = latest_flow['small_net_inflow']
        
        retail_flow_comment = ""
        if medium_net_inflow < 0 and small_net_inflow < 0:
            retail_flow_comment = "中单和小单均呈现净流出，散户资金谨慎离场"
        elif medium_net_inflow > 0 and small_net_inflow > 0:
            retail_flow_comment = "中单和小单均呈现净流入，散户资金积极介入"
        else:
            retail_flow_comment = "中单和小单流向不一致，散户资金存在分歧"
        
        # 计算主力资金占比
        total_amount = latest_flow.get('amount', 0)
        if total_amount > 0:
            main_inflow_ratio = main_net_inflow / total_amount * 100
        else:
            main_inflow_ratio = 0
        
        # 计算资金流向评分
        score = 50  # 基础分
        
        # 主力资金评分
        if main_net_inflow > 0:
            if main_inflow_ratio > 10:
                score += 25
            elif main_inflow_ratio > 5:
                score += 20
            else:
                score += 15
        else:
            if main_inflow_ratio < -10:
                score += 5
            elif main_inflow_ratio < -5:
                score += 10
            else:
                score += 15
        
        # 机构资金评分
        if super_net_inflow > 0 and large_net_inflow > 0:
            score += 20
        elif super_net_inflow < 0 and large_net_inflow < 0:
            score += 5
        else:
            score += 10
        
        # 散户资金评分
        if medium_net_inflow > 0 and small_net_inflow > 0:
            score += 10
        elif medium_net_inflow < 0 and small_net_inflow < 0:
            score += 5
        else:
            score += 7
        
        # 限制评分在0-100之间
        score = max(0, min(100, score))
        
        return {
            "status": "success",
            "main_net_inflow": main_net_inflow,
            "main_flow_status": main_flow_status,
            "main_flow_comment": main_flow_comment,
            "super_net_inflow": super_net_inflow,
            "large_net_inflow": large_net_inflow,
            "institutional_flow_comment": institutional_flow_comment,
            "medium_net_inflow": medium_net_inflow,
            "small_net_inflow": small_net_inflow,
            "retail_flow_comment": retail_flow_comment,
            "main_inflow_ratio": main_inflow_ratio,
            "avg_main_net_inflow_5d": avg_main_net_inflow,
            "fund_flow_score": score
        }
    
    except Exception as e:
        error_msg = f"分析股票 {stock_code} 资金流向失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"status": "error", "message": error_msg}

def analyze_market_context(stock_code: str) -> Dict[str, Any]:
    """
    分析市场环境
    
    Args:
        stock_code: 股票代码
    
    Returns:
        Dict[str, Any]: 市场环境分析结果
    """
    try:
        # 获取上证指数数据
        sh_index = get_stock_index_data("000001")
        # 获取深证成指数据
        sz_index = get_stock_index_data("399001")
        
        if sh_index.empty or sz_index.empty:
            logger.warning("无法获取指数数据，使用默认市场环境分析")
            return {
                "status": "warning",
                "market_trend": "震荡",
                "market_comment": "无法获取市场指数数据，市场环境分析受限",
                "market_score": 50
            }
        
        # 分析上证指数趋势
        sh_close = sh_index['close'].values
        sh_ma5 = pd.Series(sh_close).rolling(window=5).mean().iloc[-1]
        sh_ma20 = pd.Series(sh_close).rolling(window=20).mean().iloc[-1]
        
        # 分析深证成指趋势
        sz_close = sz_index['close'].values
        sz_ma5 = pd.Series(sz_close).rolling(window=5).mean().iloc[-1]
        sz_ma20 = pd.Series(sz_close).rolling(window=20).mean().iloc[-1]
        
        # 判断市场趋势
        market_trend = "震荡"
        market_comment = ""
        
        if sh_ma5 > sh_ma20 and sz_ma5 > sz_ma20:
            market_trend = "牛市"
            market_comment = "上证指数和深证成指均呈多头排列，市场整体处于牛市环境"
        elif sh_ma5 < sh_ma20 and sz_ma5 < sz_ma20:
            market_trend = "熊市"
            market_comment = "上证指数和深证成指均呈空头排列，市场整体处于熊市环境"
        else:
            market_comment = "上证指数和深证成指趋势不一致，市场处于震荡环境"
        
        # 获取行业指数数据（简化处理）
        industry_trend = "中性"
        industry_comment = "行业指数分析受限"
        
        # 综合市场评分
        score = 50  # 基础分
        
        # 市场趋势评分
        if market_trend == "牛市":
            score += 20
        elif market_trend == "震荡":
            score += 10
        else:
            score += 5
        
        # 行业趋势评分（简化）
        if industry_trend == "强势":
            score += 15
        elif industry_trend == "中性":
            score += 10
        else:
            score += 5
        
        return {
            "status": "success",
            "market_trend": market_trend,
            "market_comment": market_comment,
            "industry_trend": industry_trend,
            "industry_comment": industry_comment,
            "market_score": score
        }
    
    except Exception as e:
        error_msg = f"分析股票 {stock_code} 市场环境失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"status": "error", "message": error_msg}

def analyze_financial_data(stock_code: str, financial_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    分析财务数据
    
    Args:
        stock_code: 股票代码
        financial_data: 财务数据
    
    Returns:
        Dict[str, Any]: 财务分析结果
    """
    try:
        if not financial_data:
            return {"status": "warning", "message": "无财务数据"}
        
        # 提取财务指标
        eps = financial_data.get("eps", 0)
        net_profit_growth = financial_data.get("net_profit_growth", 0)
        revenue_growth = financial_data.get("revenue_growth", 0)
        roe = financial_data.get("roe", 0)
        gross_margin = financial_data.get("gross_margin", 0)
        net_margin = financial_data.get("net_margin", 0)
        report_date = financial_data.get("report_date", "")
        
        # 分析净利润增长率
        profit_growth_status = "正常"
        profit_growth_comment = ""
        
        if net_profit_growth > 30:
            profit_growth_status = "高速增长"
            profit_growth_comment = f"净利润同比增长{net_profit_growth:.2f}%，显示公司盈利能力强劲"
        elif net_profit_growth > 15:
            profit_growth_status = "稳健增长"
            profit_growth_comment = f"净利润同比增长{net_profit_growth:.2f}%，显示公司盈利能力稳健"
        elif net_profit_growth > 0:
            profit_growth_status = "低速增长"
            profit_growth_comment = f"净利润同比增长{net_profit_growth:.2f}%，增长动力不足"
        else:
            profit_growth_status = "负增长"
            profit_growth_comment = f"净利润同比下降{abs(net_profit_growth):.2f}%，显示公司盈利能力下滑"
        
        # 分析营收增长率
        revenue_growth_status = "正常"
        revenue_growth_comment = ""
        
        if revenue_growth > 30:
            revenue_growth_status = "高速增长"
            revenue_growth_comment = f"营收同比增长{revenue_growth:.2f}%，显示公司业务扩张迅速"
        elif revenue_growth > 15:
            revenue_growth_status = "稳健增长"
            revenue_growth_comment = f"营收同比增长{revenue_growth:.2f}%，显示公司业务稳健发展"
        elif revenue_growth > 0:
            revenue_growth_status = "低速增长"
            revenue_growth_comment = f"营收同比增长{revenue_growth:.2f}%，增长动力不足"
        else:
            revenue_growth_status = "负增长"
            revenue_growth_comment = f"营收同比下降{abs(revenue_growth):.2f}%，显示公司业务收缩"
        
        # 分析ROE
        roe_status = "正常"
        roe_comment = ""
        
        if roe > 15:
            roe_status = "优秀"
            roe_comment = f"ROE为{roe:.2f}%，显示公司资产利用效率高，股东回报良好"
        elif roe > 10:
            roe_status = "良好"
            roe_comment = f"ROE为{roe:.2f}%，显示公司资产利用效率较好"
        elif roe > 5:
            roe_status = "一般"
            roe_comment = f"ROE为{roe:.2f}%，显示公司资产利用效率一般"
        else:
            roe_comment = f"ROE为{roe:.2f}%，显示公司资产利用效率较低"
        
        # 分析毛利率
        gross_margin_status = "正常"
        gross_margin_comment = ""
        
        if gross_margin > 40:
            gross_margin_status = "优秀"
            gross_margin_comment = f"毛利率为{gross_margin:.2f}%，显示公司产品竞争力强，议价能力高"
        elif gross_margin > 30:
            gross_margin_status = "良好"
            gross_margin_comment = f"毛利率为{gross_margin:.2f}%，显示公司产品竞争力较好"
        elif gross_margin > 20:
            gross_margin_status = "一般"
            gross_margin_comment = f"毛利率为{gross_margin:.2f}%，显示公司产品竞争力一般"
        else:
            gross_margin_comment = f"毛利率为{gross_margin:.2f}%，显示公司产品竞争力较弱"
        
        # 综合财务评分
        score = 50  # 基础分
        
        # 净利润增长评分
        if net_profit_growth > 30:
            score += 20
        elif net_profit_growth > 15:
            score += 15
        elif net_profit_growth > 0:
            score += 10
        else:
            score += 5
        
        # 营收增长评分
        if revenue_growth > 30:
            score += 15
        elif revenue_growth > 15:
            score += 10
        elif revenue_growth > 0:
            score += 5
        else:
            score += 2
        
        # ROE评分
        if roe > 15:
            score += 15
        elif roe > 10:
            score += 10
        elif roe > 5:
            score += 5
        else:
            score += 2
        
        # 毛利率评分
        if gross_margin > 40:
            score += 10
        elif gross_margin > 30:
            score += 7
        elif gross_margin > 20:
            score += 5
        else:
            score += 3
        
        # 限制评分在0-100之间
        score = max(0, min(100, score))
        
        return {
            "status": "success",
            "eps": eps,
            "net_profit_growth": net_profit_growth,
            "profit_growth_status": profit_growth_status,
            "profit_growth_comment": profit_growth_comment,
            "revenue_growth": revenue_growth,
            "revenue_growth_status": revenue_growth_status,
            "revenue_growth_comment": revenue_growth_comment,
            "roe": roe,
            "roe_status": roe_status,
            "roe_comment": roe_comment,
            "gross_margin": gross_margin,
            "gross_margin_status": gross_margin_status,
            "gross_margin_comment": gross_margin_comment,
            "net_margin": net_margin,
            "report_date": report_date,
            "financial_score": score
        }
    
    except Exception as e:
        error_msg = f"分析股票 {stock_code} 财务数据失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"status": "error", "message": error_msg}

def analyze_news(stock_code: str, news_data: pd.DataFrame) -> Dict[str, Any]:
    """
    分析相关新闻
    
    Args:
        stock_code: 股票代码
        news_data: 新闻数据
    
    Returns:
        Dict[str, Any]: 新闻分析结果
    """
    try:
        if news_data.empty:
            return {"status": "warning", "message": "无相关新闻数据"}
        
        # 简单情感分析（基于关键词）
        positive_keywords = ["上涨", "增长", "利好", "增持", "回购", "业绩", "突破", "创新高", "战略合作", "扩张"]
        negative_keywords = ["下跌", "亏损", "利空", "减持", "诉讼", "监管", "处罚", "风险", "违约", "暂停"]
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for _, news in news_data.iterrows():
            content = news['content'].lower()
            title = news['title'].lower()
            
            is_positive = any(keyword in content or keyword in title for keyword in positive_keywords)
            is_negative = any(keyword in content or keyword in title for keyword in negative_keywords)
            
            if is_positive and not is_negative:
                positive_count += 1
            elif is_negative and not is_positive:
                negative_count += 1
            else:
                neutral_count += 1
        
        # 新闻情绪分析
        total_news = len(news_data)
        positive_ratio = positive_count / total_news * 100 if total_news > 0 else 0
        negative_ratio = negative_count / total_news * 100 if total_news > 0 else 0
        
        news_sentiment = "中性"
        news_comment = ""
        
        if positive_ratio > 60:
            news_sentiment = "积极"
            news_comment = f"近期新闻情绪积极，{positive_ratio:.1f}%的新闻为正面报道"
        elif negative_ratio > 60:
            news_sentiment = "消极"
            news_comment = f"近期新闻情绪消极，{negative_ratio:.1f}%的新闻为负面报道"
        else:
            news_comment = f"近期新闻情绪中性，正面新闻占比{positive_ratio:.1f}%，负面新闻占比{negative_ratio:.1f}%"
        
        # 重大事件分析
        major_events = []
        for _, news in news_data.iterrows():
            title = news['title']
            if "回购" in title or "增持" in title or "战略合作" in title or "业绩预增" in title:
                major_events.append(title)
            elif "减持" in title or "诉讼" in title or "监管" in title or "处罚" in title:
                major_events.append(title)
        
        # 综合新闻评分
        score = 50  # 基础分
        
        # 情绪评分
        if positive_ratio > 60:
            score += 20
        elif positive_ratio > 40:
            score += 15
        elif positive_ratio > 30:
            score += 10
        else:
            score += 5
        
        # 重大事件评分
        if any("回购" in event or "增持" in event for event in major_events):
            score += 10
        if any("减持" in event or "诉讼" in event for event in major_events):
            score -= 5
        
        # 限制评分在0-100之间
        score = max(0, min(100, score))
        
        return {
            "status": "success",
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "positive_ratio": positive_ratio,
            "negative_ratio": negative_ratio,
            "news_sentiment": news_sentiment,
            "news_comment": news_comment,
            "major_events": major_events,
            "news_score": score
        }
    
    except Exception as e:
        error_msg = f"分析股票 {stock_code} 新闻失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"status": "error", "message": error_msg}

def generate_stock_analysis_report(
    stock_code: str,
    basic_info: Dict[str, Any],
    realtime_data: Dict[str, Any],
    technical_analysis: Dict[str, Any],
    fund_flow_analysis: Dict[str, Any],
    market_context_analysis: Dict[str, Any],
    financial_analysis: Dict[str, Any],
    news_analysis: Dict[str, Any]
) -> str:
    """
    生成股票分析报告
    
    Args:
        stock_code: 股票代码
        basic_info: 基本信息
        realtime_data: 实时数据
        technical_analysis: 技术分析
        fund_flow_analysis: 资金流向分析
        market_context_analysis: 市场环境分析
        financial_analysis: 财务分析
        news_analysis: 新闻分析
    
    Returns:
        str: 生成的报告内容
    """
    try:
        # 1. 标题部分
        report = f"{basic_info['stock_name']}（{stock_code}）技术指标形态分析（截至{realtime_data['date'][:10]}）\n\n"
        
        # 2. 核心技术指标状态
        report += "一、核心技术指标状态\n\n"
        
        # RSI分析
        report += f"RSI（14日）{technical_analysis['rsi_status']}\n"
        report += f"当前RSI值为{technical_analysis['rsi_14']:.2f}，{technical_analysis['rsi_comment']}。\n"
        
        # 布林带分析
        report += f"布林带（BOLL）{technical_analysis['boll_status']}\n"
        report += f"股价（{technical_analysis['current_price']:.2f}元）{technical_analysis['boll_comment']}。\n"
        
        # 均线系统分析
        report += f"均线系统{technical_analysis['ma_status']}\n"
        report += f"{technical_analysis['ma_comment']}\n\n"
        
        # 3. 资金与量能验证
        report += "二、资金与量能验证\n\n"
        
        # 主力资金分析
        report += f"主力资金流向：{fund_flow_analysis['main_flow_status']}\n"
        report += f"{fund_flow_analysis['main_flow_comment']}\n"
        
        # 机构资金分析
        report += f"机构资金动向：{fund_flow_analysis['institutional_flow_comment']}\n"
        
        # 成交量分析
        report += f"量能状态：{technical_analysis['volume_status']}\n"
        report += f"{technical_analysis['volume_comment']}\n\n"
        
        # 4. 关键压力与支撑位
        report += "三、关键压力与支撑位\n\n"
        report += f"压力位：{technical_analysis['resistance1']:.2f}元（近期高点+布林带上轨）\n"
        report += f"支撑位：{technical_analysis['support1']:.2f}元（近期低点+布林带下轨）\n\n"
        
        # 5. 财务状况分析
        report += "四、财务状况分析\n\n"
        report += f"盈利能力：{financial_analysis['profit_growth_status']}\n"
        report += f"{financial_analysis['profit_growth_comment']}\n"
        report += f"财务健康度：ROE为{financial_analysis['roe']:.2f}%，{financial_analysis['roe_comment']}\n\n"
        
        # 6. 市场环境分析
        report += "五、市场环境分析\n\n"
        report += f"大盘趋势：{market_context_analysis['market_trend']}\n"
        report += f"{market_context_analysis['market_comment']}\n\n"
        
        # 7. 新闻情绪分析
        report += "六、新闻舆情分析\n\n"
        report += f"新闻情绪：{news_analysis['news_sentiment']}\n"
        report += f"{news_analysis['news_comment']}\n"
        
        if news_analysis.get('major_events'):
            report += "近期重大事件：\n"
            for event in news_analysis['major_events'][:3]:  # 只显示前3个重大事件
                report += f"• {event}\n"
        
        report += "\n"
        
        # 8. 综合结论与操作建议
        report += "七、结论与操作建议\n\n"
        
        # 综合评分
        technical_score = technical_analysis.get('technical_score', 50)
        fund_flow_score = fund_flow_analysis.get('fund_flow_score', 50)
        financial_score = financial_analysis.get('financial_score', 50)
        news_score = news_analysis.get('news_score', 50)
        market_score = market_context_analysis.get('market_score', 50)
        
        # 计算综合评分
        overall_score = (
            technical_score * 0.3 +
            fund_flow_score * 0.25 +
            financial_score * 0.2 +
            news_score * 0.15 +
            market_score * 0.1
        )
        
        # 生成结论
        if overall_score >= 80:
            conclusion = "强烈推荐"
            conclusion_comment = "技术面、资金面、基本面均表现优秀，建议积极配置"
        elif overall_score >= 65:
            conclusion = "推荐"
            conclusion_comment = "整体表现良好，建议适当配置"
        elif overall_score >= 50:
            conclusion = "中性"
            conclusion_comment = "各项指标表现一般，建议观望或少量配置"
        else:
            conclusion = "谨慎"
            conclusion_comment = "存在较多风险因素，建议谨慎操作或回避"
        
        report += f"当前综合评分为{overall_score:.1f}分，评级：{conclusion}\n"
        report += f"{conclusion_comment}\n\n"
        
        # 生成操作建议
        if technical_analysis['rsi_status'] == "超买" and technical_analysis['boll_status'] == "突破上轨":
            report += "短期：RSI接近超买区域，且股价已突破布林带上轨，可逢高减仓部分仓位，规避回调风险；\n"
        elif technical_analysis['rsi_status'] == "超卖" and technical_analysis['boll_status'] == "跌破下轨":
            report += "短期：RSI处于超卖区域，且股价已跌破布林带下轨，可考虑逢低吸纳；\n"
        else:
            report += "短期：技术指标处于正常区间，建议持有观望；\n"
        
        if technical_analysis['ma_status'] == "多头排列":
            report += "中期：均线系统呈多头排列，确立升势，回调至5日均线可考虑加仓；\n"
        elif technical_analysis['ma_status'] == "空头排列":
            report += "中期：均线系统呈空头排列，趋势向弱，反弹至5日均线可考虑减仓；\n"
        else:
            report += "中期：均线系统处于震荡状态，建议根据短期信号灵活操作；\n"
        
        report += f"风险提示：若股价跌破{technical_analysis['support1']:.2f}元且成交量萎缩，需警惕趋势反转。\n\n"
        
        # 9. 近期交易明细补充
        report += "近期交易明细补充（最近5个交易日）\n\n"
        report += "一、每日交易数据概览\n\n"
        
        # 表头
        report += "日期\t收盘价(元)\t涨跌幅\t换手率\t成交量(万手)\t成交额(亿元)\t主力资金流向(万元)\n"
        
        # 获取最近5天的交易数据
        daily_data = get_stock_daily_data(stock_code, 10)  # 获取10天数据，确保有5个交易日
        fund_flow_data = get_fund_flow_data(stock_code, 10)
        
        if not daily_data.empty:
            # 按日期倒序排列
            daily_data = daily_data.tail(5).sort_values('date', ascending=False)
            
            for _, row in daily_data.iterrows():
                date = row['date'].strftime('%Y-%m-%d')
                close = row['close']
                pct_change = row['pct_change']
                turnover = row['turnover']
                volume = row['volume'] / 10000  # 万手
                amount = row['amount'] / 100000000  # 亿元
                
                # 查找对应的资金流向数据
                fund_flow = 0
                if not fund_flow_data.empty:
                    fund_flow_row = fund_flow_data[fund_flow_data['date'] == row['date']]
                    if not fund_flow_row.empty:
                        fund_flow = fund_flow_row.iloc[0]['main_net_inflow'] / 10000  # 万元
                
                report += f"{date}\t{close:.2f}\t{pct_change:.2f}%\t{turnover:.2f}%\t{volume:.2f}\t{amount:.2f}\t{fund_flow:.2f}\n"
        else:
            report += "无法获取近期交易数据\n"
        
        report += "\n"
        
        # 10. 重要事件影响
        if news_analysis.get('major_events'):
            report += "二、重要事件影响\n\n"
            for event in news_analysis['major_events'][:3]:  # 只显示前3个重大事件
                report += f"• {event}\n"
            report += "\n"
        
        # 11. 操作建议更新
        report += "三、操作建议更新\n\n"
        report += f"短期风险：{conclusion_comment}\n"
        report += f"中期机会：若回调至{technical_analysis['support1']:.2f}元附近且量能萎缩，可视为低吸机会\n"
        report += f"关键点位：\n"
        report += f"压力位：{technical_analysis['resistance1']:.2f}元（近期高点）\n"
        report += f"支撑位：{technical_analysis['support1']:.2f}元（近期低点）\n\n"
        
        # 12. 结束语
        report += "(注：部分指标数据因数据源限制可能存在延迟，操作需结合实时行情调整。)\n"
        
        return report
    
    except Exception as e:
        error_msg = f"生成股票 {stock_code} 分析报告失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return f"【股票分析报告生成错误】{error_msg}"

# 模块初始化
try:
    logger.info("股票分析模块初始化完成")
except Exception as e:
    logger.error(f"股票分析模块初始化失败: {str(e)}", exc_info=True)