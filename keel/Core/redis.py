import redis
import json

from django.conf import settings

r = redis.StrictRedis(host=settings.REDIS_HOST, port = settings.REDIS_PORTNAME, db = settings.REDIS_DBNAME)
redis_instance = r

def create_token(varname, value, time):
    r.set(varname, value)
    r.expire(varname, time)

def get_token(varname):
    return r.get(varname)

def delete_token(varname):
    return r.delete(varname)


