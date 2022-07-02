import os
from pyngrok import ngrok

url = ngrok.connect(5001,"http",bind_tls=True).public_url
if __name__ =='__main__':
    os.system(f'python3.9 /app/jobs.py --url={url} &')
    os.system('python3.9 /app/jobs_consumer.py &')
    os.system('python3.9 /app/jobs_mailer.py &')
    os.system('python3.9 /app/jobs_web.py')