import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import logging
from hashlib import md5
client = MongoClient('test_db',27017)
test_db = client['nacool_projects']
jobs_info = test_db['jobs_info']
jobs_kw = test_db['jobs_keywords']
logger = logging.getLogger()


def get_data_from_db(query):
    jobs_list = list(jobs_info.find({
        'query': query,
        'is_expired': {'$ne': True}
    }))
    return jobs_list


def update_jobs_list(job_url, user_id=None, email=None):
    if user_id:
        user_ids = list(jobs_info.find_one({
            'job_url': job_url,
            'is_expired': {'$ne': True}
        }, {'user_ids': 1}))
        if user_ids:
            user_ids.append(user_id)
            jobs_info.update_one({'job_url': job_url},
                                {'$set': {'user_ids': user_ids}})
            return user_ids
        jobs_info.update_one({'job_url': job_url},
                            {'$set': {'user_ids': [user_id]}})
    if email:
        user_ids = list(jobs_info.find_one({
            'job_url': job_url,
            'is_expired': {'$ne': True}
        }, {'email_ids': 1}))
        if user_ids:
            user_ids.append(email)
            jobs_info.update_one({'job_url': job_url},
                                {'$set': {'email_ids': user_ids}})
            return user_ids
        jobs_info.update_one({'job_url': job_url},
                            {'$set': {'email_ids': [email]}})
    return

def get_userids(job_url):
    user_ids = list(jobs_info.find({
        'job_url':job_url,
        'is_expired': {'$ne': True}
    }, {'user_ids': 1}))
    return user_ids

def get_jobs_data(keyword):
    print(list(jobs_info.find({})))
    return list(jobs_info.find({'query':keyword}))

def get_all_jobs_list():
    return list(jobs_info.find())
def get_all_keywords():
    return list(jobs_kw.find())

def save_data(data):
    jobs_info.insert_many(data)

def check_and_update_keywords(kwords):
    keyword_check = jobs_kw.find_one({'keyword':kwords})
    if keyword_check:
        return True
    jobs_kw.insert_one({'keyword':kwords})
    return False
def check_for_duplicate_data(data):
    existing_data = jobs_info.find_one({'job_url':data['job_url']})
    if existing_data:
        return True
    return False

def scrape_page(jobs_list, query):
    job_details = []
    for job in jobs_list:
        job_detail = {}
        details = {}
        job_detail['query'] = query
        job_detail['is_expired'] = False
        job_detail['title'] = (job.find('h3').text).strip()
        job_url = job.find('a',attrs={'class':'govuk-link'})
        if job_url and job_url.get('href'):
            job_detail['job_url'] = job_url.get('href')
        else:
            continue
        if check_for_duplicate_data(job_detail):
           continue 
        u_list = job.find_all('li')
        if len(u_list) < 3:
            continue
        details['published_on'] = (u_list[0].text).strip()
        if u_list[1].find('strong'):
            details['company_name'] = (u_list[1].find('strong').text).strip()
        if u_list[1].find('span'):
            details['location'] = (u_list[1].find('span').text).strip()
        details['salary'] = (u_list[2].text).strip()
        details['extra_details'] = (job.find('p',attrs={'class':'govuk-body search-result-description'}).text).strip()
        job_detail['details'] = details
        job_details.append(job_detail)  
    if job_details:
        save_data(job_details) 


def fetch_jobs_data(query):
    try:
        url = f"https://findajob.dwp.gov.uk/search?q={query}"
        response = requests.get(url)
        response.raise_for_status()
        logger.info(f'url-hit-{url}-success')
    except Exception as e:
        logger.error(e)
        return 
    soup = BeautifulSoup(response.content,'lxml')
    pagination_div = soup.find('div',id='pager')
    pagination_item = []
    if pagination_div:
        pagination_item = pagination_div.find_all('a',attrs={'class':'govuk-link'})
    job_items = soup.find_all('div',attrs={'class':'search-result'})
    scrape_page(job_items, query)
    
    for page_url in pagination_item:
        if page_url.get('href'):
            try:
                response = requests.get(page_url.get('href'))
                response.raise_for_status()
                logger.info(f'url-hit-{page_url.get("href")}-success')
            except Exception as e:
                logger.error(e)
                break
            soup = BeautifulSoup(response.content,'lxml')
            job_items = soup.find_all('div',attrs={'class':'search-result'})
            scrape_page(job_items, query)
