
from flask import Flask, request
import telebot
from jobs_fetcher import (fetch_jobs_data, check_and_update_keywords,
update_jobs_list,get_userids,get_data_from_db, get_jobs_data)
from pymongo import MongoClient
from sql_db import insert_values_in_users,update_credits, update_keyword
import os
import argparse
import json

client = MongoClient('localhost', 27017)
test_db = client['nacool_projects']
jobs_info = test_db['jobs_info']
TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('--url')
args = parser.parse_args()
url = args.url

@bot.message_handler(commands=['start'])
def send_start_msg(message):
    chat_id = message.chat.id
    name = message.from_user.first_name
    credits = 50
    print(insert_values_in_users(name, chat_id, credits))
    bot.send_message(
        message.chat.id, "Enter the job title/titles you wanna subs seperated by ,")


@bot.message_handler(commands=['keywords'], regexp='[a-zA-z\,]+')
def send_msg_user(message):
    queries = message.text.replace('/keywords','').split(',')
    for query in queries:
        query = query.lower().strip()
        update_keyword(message.chat.id, query)
        kw_exists = check_and_update_keywords(query)
        if not kw_exists:
            fetch_jobs_data(query)
        jobs_list = get_data_from_db(query)
        for job in jobs_list:
            chat_ids = get_userids(job['job_url'])
            if not message.chat.id in chat_ids:
                data = f"<b>{job['title']}</b>\n{job['details']['company_name']}\n{job['details']['location']}\n{job['details'].get('salary')}\n{job['details']['extra_details']}\n" + \
                f"<a href='{job['job_url']}'>Job Link </a>"
                bot.send_message(chat_id=message.chat.id, text=data,
                             parse_mode='html')
                update_jobs_list(job_url=job['job_url'], user_id=message.chat.id)


@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates(
        [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@app.route('/send_notification')
def send_notification():
    data = json.loads(request.json)
    keyword = data['keyword']
    jobs_list = get_jobs_data(keyword)
    for job in jobs_list:
        job_details =f"<b>{job['title']}</b>\n{job['details']['company_name']}\n{job['details']['location']}\n{job['details'].get('salary')}\n{job['details']['extra_details']}\n" + \
                    f"<a href='{job['job_url']}'>Job Link </a>"
        bot.send_message(data['chat_id'],text=job_details,parse_mode='html')
        update_jobs_list(job_url=job['job_url'],user_id=data['chat_id'])


@app.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=url+'/'+TOKEN)
    return "!", 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
