import redis
from app.core.settings.conf import settings

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
