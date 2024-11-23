import smtplib
import settings_loader
settings = settings_loader.get_processor_settings()


def send_mail(mail, message):
    smtpObj = smtplib.SMTP('smtp.yandex.ru', 587)
    smtpObj.login(settings["mail_login"], settings["mail_login"])
    smtpObj.send_message(settings["mail_login"], mail, message)