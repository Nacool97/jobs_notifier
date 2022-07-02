import json
import pika
from jobs_fetcher import fetch_jobs_data

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='jobs_queue')

def job_consumer(ch, method, properties, body):
    data = json.loads(body.decode())
    data = data['query'].split(',')
    for d in data:
        fetch_jobs_data(d)

channel.basic_consume(queue='jobs_queue',auto_ack=True,
on_message_callback=job_consumer)
channel.start_consuming()