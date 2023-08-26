import os
import sys
from typing import List, Dict

import ray
from dotenv import load_dotenv
from loguru import logger

from redis_code_pub_sub import RedisPubSub

if not os.getenv("REDIS_URL"):
    load_dotenv()

logger.remove()  # Remove the default logger
logger.add(sys.stdout, colorize=False, backtrace=True, diagnose=True)
ray.init()


@ray.remote(num_cpus=1)
def process_message_batch(messages: List[str]):
    try:
        logger.info(f"received {len(messages)}")
        from model_call import model_call_batch
        result = model_call_batch(messages)
        r = RedisPubSub(host=os.getenv("REDIS_URL"))
        logger.info("publishing in redis")
        for message, array in zip(messages, result):
            r.push(input_val=message, array_val=array)
    except Exception as e:
        logger.error(f"{e}")


def check_for_free_worker():
    available_cpus = ray.available_resources().get('CPU', 0)
    logger.info(f"free CPU cores :- {available_cpus}")
    return available_cpus > 0


def main():
    redis_class_obj = RedisPubSub(host=os.getenv("REDIS_URL"))
    while True:
        if check_for_free_worker():
            message_val: Dict[str:List[str]] = next(redis_class_obj.subscribe("channel_batman"))
            process_message_batch.remote(message_val["message"])


if __name__ == '__main__':
    logger.info("worker started")
    main()
