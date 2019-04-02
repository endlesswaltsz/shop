import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from .celery import cel
# 输入Email地址和口令:
from_addr = '492771924@qq.com'
password = 'docxemfqbgfwbgge'
# 输入SMTP服务器地址:
smtp_server = 'smtp.qq.com'


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

@cel.task(name='emails.register_email_auth')
def register_email_auth(email, url):
    to_addr = email  # 收件人地址
    msg = MIMEText('<p>请点击以下链接来激活您的账号<a>%s</p>' % url, 'html', 'utf-8')
    msg['From'] = _format_addr(u'HY平台的提示 <%s>' % from_addr)
    msg['To'] = _format_addr(u'管理员 <%s>' % to_addr)
    msg['Subject'] = Header(u'您的账号需要激活', 'utf-8').encode()
    server = smtplib.SMTP(smtp_server, 25)  # SMTP协议默认端口是25
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()
    return 'success'


if __name__ == '__main__':
    res=register_email_auth('1164144816@qq.com','https://www.baidu.com')
    print(res)