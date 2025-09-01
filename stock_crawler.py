#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据爬取模块
负责从多个数据源获取股票实时数据、历史数据和技术指标
"""

import pandas as pd
import akshare as ak
import requests
import time
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from config import Config

# 初始化日志
logger = logging.getLogger(__name__)

def get_stock_basic_info(stock_code: str) -> Dict[str, Any]:
    """
    获取股票基本信息（公司名称、行业、上市日期等）
    
    Args:
        stock_code: 股票代码
    
    Returns:
        Dict[str, Any]: 股票基本信息
    """
    try:
        # 标准化股票代码（处理A股代码格式）
        standard_code = standardize_stock_code(stock_code)
        
        # 获取股票基本信息
        stock_info = ak.stock_zh_a_spot_em()
        
        # 查找目标股票
        target_stock = stock_info[stock_info['代码'] == standard_code]
        
        if target_stock.empty:
            logger.warning(f"未找到股票 {stock_code} 的基本信息")
            return {}
        
        # 提取基本信息
        stock_name = target_stock.iloc[0]['名称']
        industry = target_stock.iloc[0]['行业']
        area = target_stock.iloc[0]['地域']
        listing_date = target_stock.iloc[0]['上市日期']
        
        # 获取公司简介
        company_info = ak.stock_company_info_cninfo(symbol=standard_code)
        description = ""
        if not company_info.empty:
            description_row = company_info[company_info['标题'] == '经营范围']
            if not description_row.empty:
                description = description_row.iloc[0]['内容']
        
        return {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "industry": industry,
            "area": area,
            "listing_date": listing_date,
            "description": description
        }
    
    except Exception as e:
        error_msg = f"获取股票 {stock_code} 基本信息失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {}

def get_stock_daily_data(stock_code: str, days: int = 365) -> pd.DataFrame:
    """
    获取股票历史日线数据
    
    Args:
        stock_code: 股票代码
        days: 获取天数，默认1年
    
    Returns:
        pd.DataFrame: 标准化的日线数据
    """
    try:
        # 标准化股票代码
        standard_code = standardize_stock_code(stock_code)
        
        # 计算开始日期
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
        
        # 获取日线数据
        df = ak.stock_zh_a_hist(symbol=standard_code, period="daily", 
                               start_date=start_date, end_date=end_date, 
                               adjust="qfq")
        
        if df.empty:
            logger.warning(f"AkShare返回空的股票 {stock_code} 日线数据")
            return pd.DataFrame()
        
        # 标准化列名
        column_mapping = {
            '日期': 'date',
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'amount',
            '振幅': 'amplitude',
            '涨跌幅': 'pct_change',
            '涨跌额': 'price_change',
            '换手率': 'turnover'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 确保日期列为datetime类型
        df['date'] = pd.to_datetime(df['date'])
        
        # 按日期排序
        df = df.sort_values('date')
        
        # 重置索引
        df = df.reset_index(drop=True)
        
        logger.info(f"成功获取股票 {stock_code} {len(df)} 天日线数据")
        return df
    
    except Exception as e:
        error_msg = f"获取股票 {stock_code} 日线数据失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return pd.DataFrame()

def get_stock_realtime_data(stock_code: str) -> Dict[str, Any]:
    """
    获取股票实时行情数据
    
    Args:
        stock_code: 股票代码
    
    Returns:
        Dict[str, Any]: 实时行情数据
    """
    try:
        # 标准化股票代码
        standard_code = standardize_stock_code(stock_code)
        
        # 获取实时行情
        stock_info = ak.stock_zh_a_spot_em()
        
        # 查找目标股票
        target_stock = stock_info[stock_info['代码'] == standard_code]
        
        if target_stock.empty:
            logger.warning(f"未找到股票 {stock_code} 的实时行情")
            return {}
        
        # 提取实时数据
        current_data = target_stock.iloc[0]
        
        return {
            "stock_code": stock_code,
            "stock_name": current_data['名称'],
            "current_price": float(current_data['最新价']),
            "change_percent": float(current_data['涨跌幅']),
            "change_amount": float(current_data['涨跌额']),
            "volume": float(current_data['成交量']),
            "amount": float(current_data['成交额']),
            "amplitude": float(current_data['振幅']),
            "turnover": float(current_data['换手率']),
            "pe_ttm": float(current_data['市盈率-动态']),
            "pb": float(current_data['市净率']),
            "total_market_cap": float(current_data['总市值']),
            "circulating_market_cap": float(current_data['流通市值']),
            "date": datetime.now(Config.BEIJING_TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        }
    
    except Exception as e:
        error_msg = f"获取股票 {stock_code} 实时数据失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {}

def get_technical_indicators(stock_code: str, days: int = 365) -> Dict[str, Any]:
    """
    获取股票技术指标数据
    
    Args:
        stock_code: 股票代码
        days: 获取天数，默认1年
    
    Returns:
        Dict[str, Any]: 技术指标数据
    """
    try:
        # 获取历史数据
        df = get_stock_daily_data(stock_code, days)
        if df.empty:
            return {}
        
        # 计算技术指标
        indicators = {}
        
        # 1. RSI指标 (14日)
        close = df['close'].values
        delta = pd.Series(close).diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        indicators['rsi_14'] = rsi.iloc[-1]
        
        # 2. MACD指标
        ema12 = pd.Series(close).ewm(span=12, adjust=False).mean()
        ema26 = pd.Series(close).ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        
        indicators['macd'] = macd.iloc[-1]
        indicators['macd_signal'] = signal.iloc[-1]
        indicators['macd_histogram'] = histogram.iloc[-1]
        
        # 3. 布林带指标
        sma20 = pd.Series(close).rolling(window=20).mean()
        std20 = pd.Series(close).rolling(window=20).std()
        upper_band = sma20 + (std20 * 2)
        lower_band = sma20 - (std20 * 2)
        
        indicators['boll_upper'] = upper_band.iloc[-1]
        indicators['boll_middle'] = sma20.iloc[-1]
        indicators['boll_lower'] = lower_band.iloc[-1]
        
        # 4. 均线系统
        ma5 = pd.Series(close).rolling(window=5).mean()
        ma10 = pd.Series(close).rolling(window=10).mean()
        ma20 = pd.Series(close).rolling(window=20).mean()
        ma50 = pd.Series(close).rolling(window=50).mean()
        
        indicators['ma5'] = ma5.iloc[-1]
        indicators['ma10'] = ma10.iloc[-1]
        indicators['ma20'] = ma20.iloc[-1]
        indicators['ma50'] = ma50.iloc[-1]
        
        # 5. 成交量指标
        volume_ma5 = df['volume'].rolling(window=5).mean()
        volume_ma10 = df['volume'].rolling(window=10).mean()
        
        indicators['volume_ma5'] = volume_ma5.iloc[-1]
        indicators['volume_ma10'] = volume_ma10.iloc[-1]
        indicators['volume_change'] = (df['volume'].iloc[-1] / volume_ma5.iloc[-1] - 1) * 100
        
        # 6. 支撑位和压力位
        # 简化处理：使用近期高低点计算
        recent_high = df['high'].tail(20).max()
        recent_low = df['low'].tail(20).min()
        pivot = (recent_high + recent_low + df['close'].iloc[-1]) / 3
        
        resistance1 = 2 * pivot - recent_low
        support1 = 2 * pivot - recent_high
        
        indicators['resistance1'] = resistance1
        indicators['support1'] = support1
        indicators['recent_high'] = recent_high
        indicators['recent_low'] = recent_low
        
        return indicators
    
    except Exception as e:
        error_msg = f"计算股票 {stock_code} 技术指标失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {}

def get_fund_flow_data(stock_code: str, days: int = 30) -> pd.DataFrame:
    """
    获取股票资金流向数据
    
    Args:
        stock_code: 股票代码
        days: 获取天数，默认30天
    
    Returns:
        pd.DataFrame: 资金流向数据
    """
    try:
        # 标准化股票代码
        standard_code = standardize_stock_code(stock_code)
        
        # 获取资金流向数据
        df = ak.stock_money_flow_hist(symbol=standard_code)
        
        if df.empty:
            logger.warning(f"未获取到股票 {stock_code} 的资金流向数据")
            return pd.DataFrame()
        
        # 标准化列名
        column_mapping = {
            '日期': 'date',
            '主力净流入-净额': 'main_net_inflow',
            '超大单净流入-净额': 'super_net_inflow',
            '大单净流入-净额': 'large_net_inflow',
            '中单净流入-净额': 'medium_net_inflow',
            '小单净流入-净额': 'small_net_inflow'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 确保日期列为datetime类型
        df['date'] = pd.to_datetime(df['date'])
        
        # 按日期排序
        df = df.sort_values('date')
        
        # 重置索引
        df = df.reset_index(drop=True)
        
        logger.info(f"成功获取股票 {stock_code} {len(df)} 天资金流向数据")
        return df
    
    except Exception as e:
        error_msg = f"获取股票 {stock_code} 资金流向数据失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return pd.DataFrame()

def get_financial_data(stock_code: str) -> Dict[str, Any]:
    """
    获取股票财务数据
    
    Args:
        stock_code: 股票代码
    
    Returns:
        Dict[str, Any]: 财务数据
    """
    try:
        # 标准化股票代码
        standard_code = standardize_stock_code(stock_code)
        
        # 获取财务指标
        financial_indicator = ak.stock_financial_abstract(symbol=standard_code)
        
        if financial_indicator.empty:
            logger.warning(f"未获取到股票 {stock_code} 的财务指标数据")
            return {}
        
        # 提取财务指标
        financial_data = {
            "eps": financial_indicator.iloc[0]['每股收益'],
            "net_profit_growth": financial_indicator.iloc[0]['净利润同比增长率'],
            "revenue_growth": financial_indicator.iloc[0]['营业总收入同比增长率'],
            "roe": financial_indicator.iloc[0]['净资产收益率'],
            "gross_margin": financial_indicator.iloc[0]['毛利率'],
            "net_margin": financial_indicator.iloc[0]['净利率']
        }
        
        # 获取最新财报日期
        financial_data["report_date"] = financial_indicator.iloc[0]['最新财报日期']
        
        return financial_data
    
    except Exception as e:
        error_msg = f"获取股票 {stock_code} 财务数据失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {}

def get_stock_holders(stock_code: str) -> Dict[str, Any]:
    """
    获取股票股东数据
    
    Args:
        stock_code: 股票代码
    
    Returns:
        Dict[str, Any]: 股东数据
    """
    try:
        # 标准化股票代码
        standard_code = standardize_stock_code(stock_code)
        
        # 获取股东数据
        holders = ak.stock_zh_a_holder(symbol=standard_code)
        
        if holders.empty:
            logger.warning(f"未获取到股票 {stock_code} 的股东数据")
            return {}
        
        # 提取关键股东信息
        latest_holders = holders.iloc[0]  # 获取最新股东数据
        
        return {
            "total_holders": latest_holders['股东户数'],
            "avg_holding_per_holder": latest_holders['户均持股数量'],
            "avg_holding_value": latest_holders['户均持股金额'],
            "top10_holders": latest_holders['十大股东'],
            "institutional_holders": latest_holders['机构持股比例']
        }
    
    except Exception as e:
        error_msg = f"获取股票 {stock_code} 股东数据失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {}

def get_stock_news(stock_code: str, days: int = 7) -> pd.DataFrame:
    """
    获取股票相关新闻
    
    Args:
        stock_code: 股票代码
        days: 获取天数，默认7天
    
    Returns:
        pd.DataFrame: 新闻数据
    """
    try:
        # 标准化股票代码
        standard_code = standardize_stock_code(stock_code)
        
        # 获取股票名称
        basic_info = get_stock_basic_info(stock_code)
        stock_name = basic_info.get("stock_name", "")
        
        if not stock_name:
            logger.warning(f"无法获取股票 {stock_code} 名称，无法获取相关新闻")
            return pd.DataFrame()
        
        # 获取新闻数据
        news = ak.stock_news_em(symbol=stock_name)
        
        if news.empty:
            logger.warning(f"未获取到股票 {stock_code} 的相关新闻")
            return pd.DataFrame()
        
        # 标准化列名
        column_mapping = {
            '发布时间': 'publish_time',
            '标题': 'title',
            '内容': 'content',
            '新闻链接': 'url'
        }
        
        # 重命名列
        news = news.rename(columns=column_mapping)
        
        # 确保日期列为datetime类型
        news['publish_time'] = pd.to_datetime(news['publish_time'])
        
        # 过滤最近days天的新闻
        cutoff_date = datetime.now() - timedelta(days=days)
        news = news[news['publish_time'] >= cutoff_date]
        
        # 按时间排序
        news = news.sort_values('publish_time', ascending=False)
        
        # 重置索引
        news = news.reset_index(drop=True)
        
        logger.info(f"成功获取股票 {stock_code} {len(news)} 条相关新闻")
        return news
    
    except Exception as e:
        error_msg = f"获取股票 {stock_code} 新闻数据失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return pd.DataFrame()

def standardize_stock_code(stock_code: str) -> str:
    """
    标准化股票代码（A股）
    
    Args:
        stock_code: 原始股票代码
    
    Returns:
        str: 标准化后的股票代码
    """
    # 移除可能的后缀（如.SZ, .SH）
    stock_code = re.sub(r'\.[A-Z]+$', '', stock_code)
    
    # 确保6位数字
    if len(stock_code) < 6:
        stock_code = stock_code.zfill(6)
    
    return stock_code

def get_stock_index_data(index_code: str = "000001", days: int = 365) -> pd.DataFrame:
    """
    获取指数数据（用于市场环境分析）
    
    Args:
        index_code: 指数代码，默认为上证指数
        days: 获取天数，默认1年
    
    Returns:
        pd.DataFrame: 指数数据
    """
    try:
        # 计算开始日期
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
        
        # 获取指数数据
        df = ak.stock_zh_index_daily(symbol=f"sh{index_code}")
        
        if df.empty:
            logger.warning(f"未获取到指数 {index_code} 数据")
            return pd.DataFrame()
        
        # 标准化列名
        column_mapping = {
            '日期': 'date',
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'amount'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 确保日期列为datetime类型
        df['date'] = pd.to_datetime(df['date'])
        
        # 按日期排序
        df = df.sort_values('date')
        
        # 重置索引
        df = df.reset_index(drop=True)
        
        logger.info(f"成功获取指数 {index_code} {len(df)} 天数据")
        return df
    
    except Exception as e:
        error_msg = f"获取指数 {index_code} 数据失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return pd.DataFrame()

def get_stock_margin_data(stock_code: str) -> Dict[str, Any]:
    """
    获取股票融资融券数据
    
    Args:
        stock_code: 股票代码
    
    Returns:
        Dict[str, Any]: 融资融券数据
    """
    try:
        # 标准化股票代码
        standard_code = standardize_stock_code(stock_code)
        
        # 获取融资融券数据
        margin = ak.stock_margin_underlying_info(symbol="全部")
        
        # 查找目标股票
        target_stock = margin[margin['证券代码'] == standard_code]
        
        if target_stock.empty:
            logger.warning(f"未找到股票 {stock_code} 的融资融券数据")
            return {}
        
        # 提取融资融券数据
        return {
            "margin_balance": target_stock.iloc[0]['融资余额'],
            "margin_buy": target_stock.iloc[0]['融资买入额'],
            "margin_repayment": target_stock.iloc[0]['融资偿还额'],
            "short_balance": target_stock.iloc[0]['融券余额'],
            "short_sell": target_stock.iloc[0]['融券卖出量'],
            "short_repayment": target_stock.iloc[0]['融券偿还量'],
            "total_balance": target_stock.iloc[0]['担保物余额']
        }
    
    except Exception as e:
        error_msg = f"获取股票 {stock_code} 融资融券数据失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {}

# 模块初始化
try:
    logger.info("股票数据爬取模块初始化完成")
except Exception as e:
    logger.error(f"股票数据爬取模块初始化失败: {str(e)}", exc_info=True)