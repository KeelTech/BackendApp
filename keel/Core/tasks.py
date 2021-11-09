from time import sleep
from celery import shared_task, bootsteps
from kombu import Queue, Consumer, Exchange
 
# 