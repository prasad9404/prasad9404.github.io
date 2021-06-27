import os
from django.shortcuts import render
import requests
import pandas as pd
from django.http import JsonResponse
import datetime
from fbprophet import Prophet
from sklearn.metrics import r2_score
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template
from django.http import HttpResponse
from django.conf import settings
from UI import Global_Class  
import time 
   
import numpy

# Create your views here.

def IndexPage(request):
    data_state_table = getStateDataByTable("https://api.covid19india.org/data.json")
    data_india_active = india_active('https://api.covid19india.org/csv/latest/case_time_series.csv')
    data_india_recovered = india_recovered('https://api.covid19india.org/csv/latest/case_time_series.csv')
    data_india_deaths = india_deaths('https://api.covid19india.org/csv/latest/case_time_series.csv')
    data_india = get_total_india('https://api.covid19india.org/csv/latest/case_time_series.csv')
    data_india['active'] = data_india['confirm'] - (data_india['recover'] + data_india['death'])
    state = getStateDataWithStateCode("https://api.covid19india.org/data.json")
    passing = []
    for i in state:
        temp = {}
        temp['id'] = i['code']
        temp['name'] = i['state_name']
        temp['value'] = i['confirmed']
        temp['active'] = i['active']
        temp['recovered'] = i['recovered']
        temp['deaths'] = i['deaths']
        passing.append(temp)    
    return render(request,'index.html',{'State':passing,"state_table":data_state_table,"data_india":data_india,'data_india_active':data_india_active,'data_india_recovered':data_india_recovered,'data_india_deaths':data_india_deaths})

def CreatorPage(request):
    return render(request,'creator.html',{})

def predicted_data(request):
    user_input = request.GET.get('inputValue')
    State_data = pd.read_csv("https://api.covid19india.org/csv/latest/state_wise_daily.csv")
    all_data = list(State_data[user_input])
    all_date = list(State_data['Date_YMD'])
    confirmed=[]
    date=[]
    for i in range(0,len(all_data),3):        
        confirmed.append(all_data[i])
        date.append(all_date[i])
    data ={"ds":date,"y":confirmed}
    df = pd.DataFrame(data)

    df['ds'] = pd.to_datetime(df['ds'])
    #df['ds'] = df['ds'].dt.date
    #print(df)

    m = Prophet(interval_width=0.92)
    m.fit(df)
    future = m.make_future_dataframe(periods=20)
    #future.tail()

    forecast = m.predict(future)
    #print(forecast)
    #print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(20))
    dates = list(forecast['ds'])
    confirm_upper = list(map(int,forecast['yhat_upper']))
    confirm = list(map(int,forecast['yhat']))
    confirm_lower = list(map(int,forecast['yhat_lower']))
    actual = list(data['y'])

    cases = 0
    for i in range(df.count()['y']):
        if forecast['yhat_lower'][i] <= df['y'][i] <= forecast['yhat_upper'][i]:
            cases += 1
    fbaccuracy = str((cases/df.count()['y'])*100)[0:5] + "%"    

    data = {'date': dates,'fbaccuracy': fbaccuracy, 'actual': actual,'confirm_upper': confirm_upper,'confirm_lower':confirm_lower,'confirm':confirm}
    return JsonResponse(data)

def answer_me(request):
    user_input = request.GET.get('inputValue')
    State_data = pd.read_csv("https://api.covid19india.org/csv/latest/state_wise_daily.csv")
    all_data = list(State_data[user_input])
    all_date = list(State_data['Date_YMD'])
    confirm=[]
    recover=[]
    death=[]    
    date=[]

    for i in range(0,len(all_data),3):        
        confirm.append(all_data[i])        
        recover.append(all_data[i+1])
        death.append(all_data[i+2])
        date.append(all_date[i])  
        
        if i>len(all_data):
            break
    data = {'confirm': confirm,'recover': recover,'death':death,'date':date}
    return JsonResponse(data)

def SubscriptionPage(request):
    ans = ""
    obj = Global_Class.getdbconnection()
    lst=[]
    if request.method == 'POST':        
        email_to = request.POST.get('input-2')
        name = request.POST.get('input-1')
        mob = request.POST.get('input-3')
        rs = Global_Class.recordreader(obj,"Select * from users")
        for i in rs:
            lst.append(i[2])
        if(not(email_to in lst)):
            id = Global_Class.idreader(obj,"SELECT MAX(id) from users")
            Global_Class.recordmanip(obj,f"Insert into users(id,name,email,mob) values({id},'{name}','{email_to}','{mob}')")
            from_email = settings.EMAIL_HOST_USER
            Subject = "Subscription Successful"
            with open(settings.BASE_DIR + "/template/newsletters/subscribe_message.txt") as f:
                subscribe_message = f.read()
            message = EmailMultiAlternatives(subject=Subject,body=subscribe_message,from_email=from_email,to=[email_to,])
            html_template = get_template("newsletters/subscribe_email.html").render()
            message.attach_alternative(html_template,"text/html")
            message.send()
            #send_mail("Subscrption Successful", "Thanks for subscription", settings.EMAIL_HOST_USER, [email_to,])
            ans="Subscribed Succesfully"
        else:
            ans="The email already subscribed."
    return render(request,'subscription.html',{'res':ans})

def UnsubscribePage(request):
    ans = ""
    obj = Global_Class.getdbconnection()
    lst=[]
    if request.method == 'POST':        
        email_to = request.POST.get('input-1')
        rs = Global_Class.recordreader(obj,"Select * from users")
        for i in rs:
            lst.append(i[2])
        if(email_to in lst):
            Global_Class.recordmanip(obj,f"Delete from users where email='{email_to}'")
            from_email = settings.EMAIL_HOST_USER
            Subject = "Unsubscribed Succesfully"
            with open(settings.BASE_DIR + "/template/newsletters/unsubscribe_message.txt") as f:
                subscribe_message = f.read()
            message = EmailMultiAlternatives(subject=Subject,body=subscribe_message,from_email=from_email,to=[email_to,])
            html_template = get_template("newsletters/unsubscribe.html").render()
            message.attach_alternative(html_template,"text/html")
            message.send()
            ans="Unsubscribed Succesfully"
        else:
            ans="Invalid Email"
    return render(request,'unsubscribe.html',{'res':ans})

def UpdatePage(request):
    if request.method == 'POST':
        obj = Global_Class.getdbconnection()
        email_to=[]
        data_india = get_total_india('https://api.covid19india.org/csv/latest/case_time_series.csv')
        actives = data_india['confirm'] - (data_india['recover'] + data_india['death'])
        confirmed = data_india['confirm'] 
        recovered = data_india['recover']
        deceased = data_india['death']
        data_india_active = india_active('https://api.covid19india.org/csv/latest/case_time_series.csv')
        data_india_recovered = india_recovered('https://api.covid19india.org/csv/latest/case_time_series.csv')
        data_india_deaths = india_deaths('https://api.covid19india.org/csv/latest/case_time_series.csv')
        confirm = data_india_active['active'][-1]
        date = data_india_active['date'][-1]
        recover = data_india_recovered['recovered'][-1]
        decease = data_india_deaths['death'][-1]

        data = f"Covid-19 Statistics on {date} \n\n Confirmed: {confirm} \n\n  Recovered:  {recover} \n\n  Deceased:  {decease} \n\n Statistics Till Date"
        data += f"\n\n Confirmed: {confirmed} \n\n Active:{actives} \n\n  Recovered: {recovered} \n\n Deceased:  {deceased} \n\n If you wish to unsubscribe, visit this link: Unsubscribe."
        data += f" Warm Regards, \n\n Admin,\nCovid19inIndia\nAdmin@covid19inindia.in\nwww.covid19inindia.in"    
        rs = Global_Class.recordreader(obj,"Select * from users")
        update_message=data        
        for i in rs:
            email_to.append(i[2])
        from_email = settings.EMAIL_HOST_USER
        Subject = "Todays Covid-19 Update Report From Covid19inindia.in " 
        message = EmailMultiAlternatives(subject=Subject,body=update_message,from_email=from_email,to=email_to)
        html_template = get_template("newsletters/daily_updates.html").render(context={'date':date,'confirm':confirm,'recover':recover,'death':decease,'confirmed':confirmed,'recovered':recovered,'deaths':deceased,'active':actives})
        message.attach_alternative(html_template,"text/html")
        message.send()
        return render(request,'subscription.html',{})

    return render(request,'update.html',{})

def DataTablePage(request):
    return render(request,'datatable.html',{})


# State Map Data 
def getStateDataWithStateCode(url):
    response = requests.get(url)
    data = response.json()
    state_data_with_code = []
    for state in (data['statewise']):
        if state['state'] == 'Total' or state['state'] == 'State Unassigned':
            pass
        else:
            temp = {}
            temp['state_name']= state['state']
            if state['statecode'].upper()=='MN':
                temp['code'] ="IN."+'MNL'
            else:
                temp['code'] ="IN." + state['statecode'].upper()
            temp['active']= state['active']
            temp['confirmed'] = state['confirmed']
            temp['deaths'] = state['deaths']
            temp['recovered']= state['recovered']
            state_data_with_code.append(temp)
    return state_data_with_code

#State Data As Table
def getStateDataByTable(url):
    response = requests.get(url)
    data = response.json()
    state_data_table = []
    count=1
    for state in (data['statewise']):
        if state['state'] == 'State Unassigned':
            pass
        else:
            if state['state'] == 'Total':
                lst = [count,'India',state['confirmed'],state['active'],state['recovered'],state['deaths'],state['statecode']]
                state_data_table.append(lst)
                count += 1
            else:
                lst = [count,state['state'],state['confirmed'],state['active'],state['recovered'],state['deaths'],state['statecode']]
                state_data_table.append(lst)
                count += 1
    State_data = pd.read_csv("https://api.covid19india.org/csv/latest/state_wise_daily.csv")
    col= list(State_data.columns) 
    colname = [col[i] for i in range(4,len(col))]   
    last_update = {}
    for j in colname:
            last_update[j] = list(State_data[j].tail(3))

    return {'state_data_table':state_data_table,'last_update':last_update}

#India Total Data Value
def get_total_india(url):
    df = pd.read_csv(url)
    #    print(df[['Date',"Daily Recovered"]].tail(6))
    india_c = list(df['Total Confirmed'])
    india_d = list(df['Total Deceased'])
    india_r = list(df['Total Recovered'])

    return {'confirm': india_c[-1], 'death': india_d[-1],'recover':india_r[-1]}

#India Chart Value
def india_active(url):
    df = pd.read_csv(url)
    #    print(df[['Date',"Daily Confirmed"]].tail(6))
    india_date= list(df['Date_YMD'])
    india_confirmed_cases = list(df['Daily Confirmed'])
    india_total_confirmed_cases = list(df['Total Confirmed'])    
    return {'date': india_date, 'active': india_confirmed_cases,'confirm':india_total_confirmed_cases}

def india_recovered(url):
    df = pd.read_csv(url)
    #    print(df[['Date',"Daily Recovered"]].tail(6))
    india_date= list(df['Date'])
    india_confirmed_cases = list(df['Daily Recovered'])
    india_total_confirmed_cases = list(df['Total Recovered'])    

    return {'date': india_date, 'recovered': india_confirmed_cases,'total_recovered':india_total_confirmed_cases}
def india_deaths(url):
    df = pd.read_csv(url)
    #    print(df[['Date',"Daily Recovered"]].tail(6))
    india_date= list(df['Date'])
    india_confirmed_cases = list(df['Daily Deceased'])
    india_total_confirmed_cases = list(df['Total Deceased'])    

    return {'date': india_date, 'death': india_confirmed_cases,'total_death':india_total_confirmed_cases} 
