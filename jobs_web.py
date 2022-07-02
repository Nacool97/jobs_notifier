import json
import os
from flask import Flask, redirect, request, render_template, url_for, session
from flask_session import Session   
from flask_mail import Mail, Message
from authenticate import auth
from sql_db import (get_data, insert_data, get_credit, get_keywords, 
update_credits, update_keyword, toggle_email)
from keyword_queue import queue_message
from jobs_fetcher import fetch_jobs_data, get_jobs_data, update_jobs_list, get_all_jobs_list, check_and_update_keywords
web = Flask(__name__)

mail_username = os.environ.get('MAIL_USERNAME')
mail_password = os.environ.get('MAIL_PASSWORD')
web.config['MAIL_SERVER']='smtp.gmail.com'
web.config['MAIL_PORT'] = 465
web.config['MAIL_USERNAME'] = mail_username
web.config['MAIL_PASSWORD'] = mail_password
web.config['MAIL_USE_TLS'] = False
web.config['MAIL_USE_SSL'] = True
mail = Mail(web)

web.config["SESSION_TYPE"] = "filesystem"
Session(web)

@web.route('/' ,methods=['GET'])
def index():
    if not session.get('email'):
       return render_template('login.html')
    send_mail = get_data(email=session['email'])
    if send_mail:
        send_mail = send_mail[8]
    credit = get_credit(email=session['email'])
    sub_keywords = get_keywords(email=session['email'])
    jobs_data = []
    if sub_keywords:
        sub_keywords = sub_keywords.split(',')
        for kw in sub_keywords:
            jobs_data.extend(get_jobs_data(kw))
    print(jobs_data)
    return render_template('index.html',user=session['email'], 
    keyword=sub_keywords, credits_left = credit, data=jobs_data,send_email=send_mail)


@web.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'GET':
        return render_template('signup.html')
    if request.method == 'POST':
        print(request.form)
        name = request.form['name']
        email = request.form['email']
        password = request.form['psw']
        password_rep = request.form['psw-repeat']
        print(email,password)
        if password != password_rep:
            return render_template('signup.html', error="Password do not match")
        insert_data(name=name,email=email,password=password)
        session['email'] = email
        return redirect(url_for('index'))


@web.route('/login',methods=['GET','POST'])
def login_page():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('psw')
        valid = auth(password,email)
        print(valid)
        if valid:
            session['email'] = email
            return redirect(url_for('index'))
        return render_template('login.html', error = "bad credentials")
    

@web.route('/logout',methods=['GET','POST'])
def logout():
    session['email'] = None
    
    return render_template('login.html',error="Logged out")

@web.route('/subs',methods=['POST'])
def keywords_subs():
    keyword = request.form.get('keyword').lower()
    credit = get_credit(email=session['email'])
    if not credit:
        return redirect(url_for('index'))
    credit -= 1
    update_keyword(keyword,email=session['email'])
    check_and_update_keywords(keyword)
    update_credits(credit,email=session['email'])
    keywords = get_keywords(email=session['email'])
    fetch_jobs_data(keywords)
    return redirect(url_for('index'))

@web.route('/send_mail',methods=['POST'])
def send_mail():
    keyword = None
    if request.is_json:
        print(request.json)
        email = json.loads(request.json)['email']
        keyword = json.loads(request.json)['keyword']
    else:
        email = session['email']
    toggle_email(email)
    send_mail_notification(email, keyword)
    return redirect(url_for('index'))

@web.route('/donot_send_mail',methods=['POST'])
def donot_send_email():
    email = session['email']
    toggle_email(email)
    return redirect(url_for('index'))

def send_mail_notification(email, keyword=None):
    if keyword:
        jobs_list = get_jobs_data(keyword)
    else:
        jobs_list = get_all_jobs_list()
    send_list = []
    msg = None
    for jobs in jobs_list:
        if jobs.get('email_ids') and email in jobs.get('email_ids'):
            continue
        msg = Message(
                subject='Jobs Update',
                sender ='Jobs Update',
                recipients = [email]
               )
        jobs_details = {'title' : jobs['title'],
        'name' : jobs['details']['company_name'],
        'salary' : jobs['details'].get('salary'),
        'location' : jobs['details']['location'],
        'details':jobs['details']['extra_details'],
        'url':jobs['job_url']}
        send_list.append(jobs_details)
        update_jobs_list(job_url=jobs['job_url'],email=email)
    if msg:
        msg.html = render_template('email_temp.html',data = send_list)
        mail.send(msg)
@web.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

if __name__ == '__main__':
    web.run(host='0.0.0.0', port=5000, debug=True)
