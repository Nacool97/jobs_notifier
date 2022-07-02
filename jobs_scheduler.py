from jobs_fetcher import fetch_jobs_data
from pymongo import MongoClient

client = MongoClient('localhost',27017)
test_db = client['nacool_projects']
jobs_kw = test_db['jobs_keywords']
def main():
    kw_lists = list(jobs_kw.find())
    for kw in kw_lists:
        fetch_jobs_data(kw)
        
if __name__ == '__main__':
    main()

