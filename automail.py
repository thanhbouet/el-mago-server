from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

import smtplib
import os


def connect():
    smtpO = smtplib.SMTP('smtp.gmail.com', 587)
    smtpO.ehlo()
    smtpO.starttls()
    smtpO.login('dinhthanhzula@gmail.com','bwvcodzyryherhvj')
    return smtpO
    

def buid_msg_content(subject="Verify El Mago Account", text_message = ""):
    msg = MIMEMultipart()
    msg['SUBJECT'] = subject
    msg.attach(MIMEText(text_message))
    
    return msg
    
target = ["dthanhuet@gmail.com","obhnaht@gmail.com"]

def send_email(target,msg):
    pass
    # try:
    #     smtp.sendmail(from_addr="dthanhuet@gmail.com",
    #               to_addrs=target, msg=msg.as_string())
    # except Exception:
        # pass
        # smtp = connect()
        # send_email(target,msg)

def quit():
    smtp.quit()
    
smtp = connect()    

if __name__ == '__main__':
    send_email(target=target,msg=buid_msg_content(text_message="Hello cai bo"))