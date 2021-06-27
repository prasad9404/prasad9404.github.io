import schedule
import time
from UI import Global_Class   
from django.core.mail import send_mail

def job():
    obj = Global_Class.getdbconnection()
    rs = Global_Class.recordreader(obj,"select email from users")
    for i in rs:
        print(i)
    email_to = [i[0] for i in rs]
    send_mail("Subscrption Successful", "Thanks for subscription", settings.EMAIL_HOST_USER, email_to)        
        
schedule.every().day.at("19:52").do(job)
while True:
    schedule.run_pending()
    time.sleep(1)
