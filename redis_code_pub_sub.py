import orjson
from typing import Dict

import numpy as np
import redis
from numpy import array


class RedisPubSub:
    def __init__(self, host='localhost', port=6379):
        self.redis_client = redis.Redis(host=host, port=port, db=0)

    def publish(self, channel: str, message: Dict):
        self.redis_client.publish(channel, orjson.dumps(message))

    def subscribe(self, channel):
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(channel)

        for message in pubsub.listen():
            if message['type'] == 'message':
                yield orjson.loads(message['data'].decode('utf-8'))

    def push(self, input_val: str, array_val: array):
        array_bytes = array_val.tobytes()
        self.redis_client.hset(input_val, 'data', array_bytes)
        self.redis_client.hset(input_val, 'dtype', str(array_val.dtype))
        self.redis_client.hset(input_val, 'shape', str(array_val.shape))
        self.redis_client.expire(input_val, 60 * 60)

    def pull(self, input_val: str):
        retrieved_array_bytes = self.redis_client.hget(input_val, 'data')
        if retrieved_array_bytes:
            retrieved_dtype = np.dtype(self.redis_client.hget(input_val, 'dtype').decode('utf-8'))
            str_shape = self.redis_client.hget(input_val, 'shape').decode('utf-8')[1:-1].split(',')
            str_shape = [x for x in str_shape if x]

            retrieved_shape = tuple(map(int, str_shape))

            retrieved_array = np.frombuffer(retrieved_array_bytes, dtype=retrieved_dtype).reshape(retrieved_shape)

            return retrieved_array
        return None

    def __del__(self):
        self.redis_client.close()
