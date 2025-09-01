from email_sender import test_email_connection

if __name__ == "__main__":
    print("正在测试邮件服务器连接...")
    success = test_email_connection()
    
    if success:
        print("✅ 邮件服务器连接测试成功！")
    else:
        print("❌ 邮件服务器连接测试失败，请检查配置")
