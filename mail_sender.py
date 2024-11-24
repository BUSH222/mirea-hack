import smtplib
import settings_loader
settings = settings_loader.get_processor_settings()


def send_mail(mail, message):
    print(settings['mail_login'])
    print(settings['mail_password'])
    smtpObj = smtplib.SMTP('smtp.gmail.com', 25)
    smtpObj.ehlo()
    smtpObj.starttls()
    smtpObj.login(settings["mail_login"], settings["mail_password"])
    smtpObj.sendmail([settings["mail_login"], ], [mail, ], message)
    smtpObj.quit()


if __name__ == '__main__':
    send_mail(settings['admin_email'], 'HELP ME')
