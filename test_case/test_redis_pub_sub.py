import json
import unittest
from unittest.mock import patch

import numpy as np

from redis_code_pub_sub import RedisPubSub


class TestRedisPubSub(unittest.TestCase):

    @patch('redis.Redis')
    def test_publish(self, MockRedis):
        client = MockRedis()
        pubsub = RedisPubSub()

        # Perform the action
        pubsub.publish('c', {'message': 'Hello'})

        client.publish.assert_called_with('c', json.dumps({'message': 'Hello'}))

    @patch('redis.Redis')
    def test_push_pull(self, MockRedis):
        client = MockRedis()
        pubsub = RedisPubSub()

        array = np.array([[1, 2, 3]])

        pubsub.push('a', array)

        array_bytes = array.tobytes()
        client.hset.assert_any_call('a', 'data', array_bytes)
        client.hset.assert_any_call('a', 'dtype', str(array.dtype))
        client.hset.assert_any_call('a', 'shape', str(array.shape))
        client.expire.assert_called_with('a', 60 * 60)

        client.hget.side_effect = [array_bytes, str(array.dtype).encode(), str(array.shape).encode()]
        retrieved_array = pubsub.pull('a')
        print(array)
        self.assertTrue(np.array_equal(retrieved_array, array))


if __name__ == '__main__':
    unittest.main()
