import kombu
from celery import bootsteps
from config.celery import app
from django.conf import settings
from kombu import Connection

conn_broker = Connection(settings.CELERY_BROKER_URL)


class Exchange(kombu.Exchange):

    def publisher(self, message, exchange, routing_key, **kwargs):
        with Connection(conn_broker) as conn:
            conn.ensure_connection()
            conn.ensure_channel()
            simple_queue = conn.SimpleQueue('simple_queue')
            simple_queue.put(message, exchange=exchange, routing_key=routing_key, serializer='json', **kwargs)
            simple_queue.close()

    def subscriber(self):
        with Connection(conn_broker) as conn:
            simple_queue = conn.SimpleQueue('simple_queue')
            message = simple_queue.get(block=True, timeout=1)
            print(f'Received: {message.payload}')
            message.ack()
            simple_queue.close()


# # setting publisher
# with app.pool.acquire(block=True) as conn:
#     exchange = kombu.Exchange(
#         name='myexchange',
#         type='direct',
#         durable=True,
#         channel=conn,
#     )
#     exchange.declare()

#     queue = kombu.Queue(
#         name='myqueue',
#         exchange=exchange,
#         routing_key='mykey',
#         channel=conn,
#         message_ttl=600,
#         queue_arguments={
#             'x-queue-type': 'classic'
#         },
#         durable=True
#     )
#     queue.declare()


# # setting consumer
# class MyConsumerStep(bootsteps.ConsumerStep):

#     def get_consumers(self, channel):
#         return [kombu.Consumer(channel,
#                                queues=[queue],
#                                callbacks=[self.handle_message],
#                                accept=['json'])]

#     def handle_message(self, body, message):
#         print('Received message: {0!r}'.format(body))
#         message.ack()


# app.steps['consumer'].add(MyConsumerStep)
