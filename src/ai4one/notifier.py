import smtplib
from email.mime.text import MIMEText
from email.header import Header
from typing import Sequence


class Notifier:
    """
    Base class for notifier services. This class defines a common interface for sending notifications.
    """
    
    def send(self, *args, **kwargs):
        """
        Sends a notification. This method must be implemented by subclasses.
        """
        raise NotImplementedError


class QQEmailNotifier(Notifier):
    """
    Notifier for sending emails using QQ's SMTP server.

    Example usage:
        # Initialize with your QQ email address and authorization code
        qq_notifier = QQEmailNotifier(from_addr="your_email@qq.com", qq_code="your_qq_authorization_code")
        
        # Send an email
        success, error_message = qq_notifier.send(
            to_addrs="recipient@example.com",
            title="Test Email",
            content="This is a test email sent from QQ Email Notifier."
        )
        if success:
            print("Email sent successfully.")
        else:
            print(f"Failed to send email: {error_message}")
    """

    def __init__(self, from_addr: str, qq_code: str):
        """
        Initializes the QQEmailNotifier with the sender's email address and QQ email authorization code.
        
        :param from_addr: The email address of the sender (QQ email).
        :param qq_code: The authorization code (app password) for the QQ account.
        """
        super().__init__()
        self.from_addr = from_addr  # The sender's email address.
        self.qq_code = qq_code  # QQ authorization code (app password).
        self.stmp = None  # SMTP connection object (initially None).

    def login(self):
        """
        Logs into the QQ SMTP server using the provided credentials.
        This method is called internally before sending an email.
        """
        if self.stmp:
            return  # If already logged in, do nothing.
        
        smtp_server = "smtp.qq.com"  # QQ's SMTP server address.
        smtp_port = 465  # SMTP port for SSL connection.

        # Set up the SMTP server connection.
        self.stmp = smtplib.SMTP_SSL(smtp_server, smtp_port)
        self.stmp.login(self.from_addr, self.qq_code)  # Log in to the server using the email and authorization code.

    def send(
        self,
        to_addrs: str | Sequence[str],  # Recipient(s) email address (string or list of emails).
        title: str,  # Subject of the email.
        content: str,  # Content of the email.
        from_user: str = "ai4one",  # Name to be displayed as the sender.
        to_user: str = "me",  # Name to be displayed as the recipient.
    ) -> tuple[bool, str]:
        """
        Sends an email through the QQ SMTP server.

        :param to_addrs: The recipient(s) email address (string or list of emails).
        :param title: The subject of the email.
        :param content: The body of the email.
        :param from_user: The name to display as the sender (default: "ai4one").
        :param to_user: The name to display as the recipient (default: "me").
        
        :return: A tuple (success_flag, error_message). If the email is sent successfully, success_flag is True and error_message is empty. If an error occurs, success_flag is False and error_message contains the error message.
        """
        self.login()  # Log in to the SMTP server before sending the email.

        # Compose the email message.
        message = MIMEText(content, "plain", "utf-8")  # Email body content.
        message["From"] = Header(f"{from_user} <{self.from_addr}>")  # Sender's email address.
        message["To"] = Header(to_user, "utf-8")  # Recipient's name.
        message["Subject"] = Header(title, "utf-8")  # Email subject.

        try:
            self.stmp.sendmail(self.from_addr, to_addrs, message.as_string())  # Send the email.
            return True, ""  # If the email is sent successfully, return True with no error message.
        except Exception as e:
            return False, str(e)  # If an error occurs, return False and the error message.
