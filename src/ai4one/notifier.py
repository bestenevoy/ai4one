import smtplib
from email.mime.text import MIMEText
from email.header import Header
from typing import Sequence


class Notifier:

    def send(self, *args, **kwargs):
        raise NotImplementedError


class QQEmailNotifier(Notifier):

    def __init__(self, from_addr: str, qq_code: str):
        """
        from_addr = ''  # 邮件发送账号
        qqCode = ''  # 授权码（这个要填自己获取到的）
        """
        super().__init__()
        self.from_addr = from_addr
        self.qq_code = qq_code
        self.stmp = None

    def login(self):
        if self.stmp:
            return
        smtp_server = "smtp.qq.com"
        smtp_port = 465

        # 配置服务器
        self.stmp = smtplib.SMTP_SSL(smtp_server, smtp_port)
        self.stmp.login(self.from_addr, self.qq_code)

    def send(
        self,
        to_addrs: str | Sequence[str],
        title,
        content,
        from_user="ai4one",
        to_user="me",
    ) -> tuple[bool, str]:
        self.login()

        # 组装发送内容
        message = MIMEText(content, "plain", "utf-8")  # 发送的内容
        message["From"] = Header(f"{from_user} <{self.from_addr}>")  # 发件人
        message["To"] = Header(to_user, "utf-8")  # 收件人
        message["Subject"] = Header(title, "utf-8")  # 邮件标题
        try:
            self.stmp.sendmail(self.from_addr, to_addrs, message.as_string())
            return True, ""
        except Exception as e:
            return False, str(e)
