import json
import re
import time
from sql_db import get_all_users, get_keywords
from jobs_fetcher import fetch_jobs_data, get_all_keywords
import requests
from jobs import url
def check_for_new_jobs_in_db(keyword):
   user_list = get_all_users()
   for user in user_list:
      email_id = user[5]
      chat_id = user[4]
      if not email_id and not chat_id:
         continue
      if re.search('[a-z0-9\.]+@[a-z\.]+',email_id):
         user_kw = get_keywords(email=email_id)
         if not user_kw:
            continue
         if keyword in user_kw.split(','):
            requests.post(url='http://localhost:5001/send_mail',json=json.dumps({'email':email_id,'keyword':keyword}))
      if chat_id:
         user_kw = get_keywords(user_id=chat_id)
         if not user_kw:
            continue
         if keyword in user_kw.split(','):   
            requests.post(url=url+'/send_notification',json=json.dumps({'chat_id':chat_id,'keyword':keyword}))
if __name__ =='__main__':
   while True:
      keyword_list = get_all_keywords()
      for keyword in keyword_list:
         fetch_jobs_data(query=keyword)
         check_for_new_jobs_in_db(keyword)
      time.sleep(3600)