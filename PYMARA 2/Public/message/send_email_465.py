import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

class SendEmail:
    def __init__(self, my_email, my_pass, list_addr):
        # 发件人邮箱账号
        self.my_email = my_email
        # 发件人邮箱授权码，授权码是用于登录第三方邮件客户端的专用密码。
        self.my_pass = my_pass
        # 收件人邮箱账号
        self.addressee = list_addr

    def mail(self, email_msg, subject):
        result = True
        try:
            # 　邮件内容
            msg = MIMEText(_text=email_msg, _subtype='html', _charset='utf-8')

            # 发件人 (name, address)
            msg['From'] = formataddr(("PyMara博客", self.my_email))
            # 收件人 (name, address)
            for addr in self.addressee:
                msg['To'] = formataddr(addr)
            # 邮件主题
            msg['Subject'] = subject

            list_addrs = [addr[1] for addr in self.addressee]
            server = smtplib.SMTP_SSL("smtp.qq.com", 465)
            server.login(self.my_email, self.my_pass)
            server.sendmail(self.my_email, list_addrs, msg.as_string())
            server.quit()
        except Exception as e:
            result = False
            print("---- send email error -----")
            print(e)

        return result


if __name__ == '__main__':
    from_email = "1102225813@qq.com"
    from_pass = "evstyhswxsawjada"
    list_addrs = [("陈卓小号", "783753616@qq.com")]
    email_text = "<h1>这是测试邮件03<br>用户注册短信验证码发送失败<br>原因: xxxxx</h1>"

    email_obj = SendEmail(my_email= from_email, my_pass=from_pass, list_addr=list_addrs)
    res = email_obj.mail(email_text, "【PyMara报错邮件】")

    if res:
        print("邮件发送成功")
    else:
        print("邮件发送失败")

