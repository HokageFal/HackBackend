import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def send_email_sync(to_email: str, subject: str, body: str, is_html: bool = True):
    logger.info(
        "Starting email sending",
        operation="send_email_sync",
        to_email=to_email,
        subject=subject,
        is_html=is_html,
        smtp_host=settings.SMTP_HOST,
        smtp_port=settings.SMTP_PORT
    )
    
    try:
        # Создаем сообщение
        if is_html:
            msg = MIMEMultipart()
            msg.attach(MIMEText(body, "html", "utf-8"))
        else:
            msg = MIMEText(body, "plain", "utf-8")
        
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_USER
        msg["To"] = to_email
        
        # Выбираем метод подключения в зависимости от порта
        if settings.SMTP_PORT == 465:
            # SSL соединение
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                smtp.sendmail(settings.SMTP_USER, [to_email], msg.as_string())
        else:
            # STARTTLS соединение
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
                smtp.starttls()
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                smtp.sendmail(settings.SMTP_USER, [to_email], msg.as_string())
        
        logger.info(
            "Email sent successfully",
            operation="send_email_sync",
            to_email=to_email,
            subject=subject
        )
        
        return True
        
    except Exception as e:
        logger.error(
            "Failed to send email",
            operation="send_email_sync",
            to_email=to_email,
            subject=subject,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise e


def create_otp_email_template(username: str, otp_code: str) -> str:
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2c3e50;">Код подтверждения</h2>
            
            <p>Здравствуйте, {username}!</p>
            
            <p>Ваш код подтверждения для AI Landing Generator:</p>
            
            <div style="background-color: #f8f9fa; border: 2px solid #e9ecef; 
                       border-radius: 8px; padding: 20px; text-align: center; 
                       margin: 20px 0;">
                <h1 style="color: #007bff; font-size: 32px; margin: 0; 
                          letter-spacing: 5px; font-family: 'Courier New', monospace;">
                    {otp_code}
                </h1>
            </div>
            
            <p><strong>Важно:</strong></p>
            <ul>
                <li>Код действителен в течение {settings.OTP_EXPIRE_MINUTES} минут</li>
                <li>Не передавайте код третьим лицам</li>
                <li>Если вы не запрашивали этот код, проигнорируйте письмо</li>
            </ul>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            
            <p style="color: #666; font-size: 12px;">
                Это автоматическое сообщение, не отвечайте на него.
            </p>
        </div>
    </body>
    </html>
    """


def create_password_reset_email_template(username: str, otp_code: str) -> str:
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2c3e50;">Сброс пароля</h2>
            
            <p>Здравствуйте, {username}!</p>
            
            <p>Вы запросили сброс пароля для вашего аккаунта в AI Landing Generator.</p>
            
            <p>Ваш код для сброса пароля:</p>
            
            <div style="background-color: #fff3cd; border: 2px solid #ffc107; 
                       border-radius: 8px; padding: 20px; text-align: center; 
                       margin: 20px 0;">
                <h1 style="color: #856404; font-size: 32px; margin: 0; 
                          letter-spacing: 5px; font-family: 'Courier New', monospace;">
                    {otp_code}
                </h1>
            </div>
            
            <p><strong>Важно:</strong></p>
            <ul>
                <li>Код действителен в течение {settings.OTP_EXPIRE_MINUTES} минут</li>
                <li>Не передавайте код третьим лицам</li>
                <li>Если вы не запрашивали сброс пароля, немедленно смените пароль</li>
                <li>После смены пароля вы будете разлогинены на всех устройствах</li>
            </ul>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            
            <p style="color: #666; font-size: 12px;">
                Это автоматическое сообщение, не отвечайте на него.
            </p>
        </div>
    </body>
    </html>
    """


def create_psychologist_credentials_email_template(
    full_name: str,
    email: str,
    password: str,
    access_until: str = None
) -> str:
    access_info = f"<li>Доступ действителен до: <strong>{access_until}</strong></li>" if access_until else ""
    
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2c3e50;">Добро пожаловать в ПрофДНК!</h2>
            
            <p>Здравствуйте, {full_name}!</p>
            
            <p>Для вас был создан аккаунт психолога на платформе ПрофДНК.</p>
            
            <div style="background-color: #e7f3ff; border: 2px solid #2196F3; 
                       border-radius: 8px; padding: 20px; margin: 20px 0;">
                <h3 style="color: #1976D2; margin-top: 0;">Ваши данные для входа:</h3>
                <p style="margin: 10px 0;">
                    <strong>Email:</strong> {email}
                </p>
                <p style="margin: 10px 0;">
                    <strong>Пароль:</strong> <code style="background: #fff; padding: 5px 10px; 
                    border-radius: 4px; font-size: 14px;">{password}</code>
                </p>
            </div>
            
            <p><strong>Важная информация:</strong></p>
            <ul>
                <li>Сохраните эти данные в безопасном месте</li>
                <li>Рекомендуем сменить пароль после первого входа</li>
                {access_info}
                <li>Не передавайте данные доступа третьим лицам</li>
            </ul>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:8000/docs" 
                   style="background-color: #2196F3; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Войти в систему
                </a>
            </div>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            
            <p style="color: #666; font-size: 12px;">
                Это автоматическое сообщение. Если у вас возникли вопросы, 
                свяжитесь с администратором.
            </p>
        </div>
    </body>
    </html>
    """
