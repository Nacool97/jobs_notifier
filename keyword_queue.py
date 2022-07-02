import pika


def queue_message(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='jobs_queue')
    channel.basic_publish(exchange='',
    routing_key='jobs_queue',
    body=message)
    print('[0] Sent message')
    connection.close()