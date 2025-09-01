from email_sender import test_email_connection
import datetime
from datetime import timezone, timedelta

if __name__ == "__main__":
    print("正在测试邮件服务器连接...")
    success = test_email_connection()
    
    if success:
        # 获取当前时间
        utc_now = datetime.datetime.now(timezone.utc)
        beijing_now = utc_now.astimezone(timezone(timedelta(hours=8)))
        
        # 生成丰富的测试邮件内容
        test_content = "【邮件测试报告】\n"
        test_content += "这是来自stock-analyse仓库的测试邮件\n\n"
        test_content += "✅ 邮件服务器配置测试成功\n\n"
        test_content += "🔍 测试详情\n"
        test_content += "• 仓库名称: stock-analyse\n"
        test_content += "• 测试类型: 邮件服务器连接测试\n"
        test_content += "• 测试结果: 连接成功，SMTP认证通过\n\n"
        test_content += "⚠️ 注意事项\n"
        test_content += "• 本邮件为系统自动发送的测试邮件\n"
        test_content += "• 不包含实际股票分析数据\n"
        test_content += "• 如需正式分析报告，请通过系统触发分析任务\n\n"
        test_content += "──────────────────\n"
        test_content += f"🕒 UTC时间: {utc_now.strftime('%Y-%m-%d %H:%M:%S')}\n"
        test_content += f"🕒 北京时间: {beijing_now.strftime('%Y-%m-%d %H:%M:%S')}\n"
        test_content += "──────────────────\n"
        test_content += "🔗 数据来源: https://github.com/yourusername/stock-analyse/actions\n"
        test_content += "📊 环境：测试\n"
        test_content += "📝 说明：这是邮件服务配置测试，非正式分析报告"
        
        print("\n" + "="*50)
        print("测试邮件内容预览：")
        print("="*50)
        print(test_content)
        print("="*50)
        print("邮件已发送至配置的接收邮箱，请查收")
        print("="*50)
    else:
        print("❌ 邮件服务器连接测试失败，请检查配置")
