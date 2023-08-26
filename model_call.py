from typing import List

import numpy as np
from loguru import logger


def model_call_batch(input_batch_sent: List[str]):
    logger.info("processing through model")
    return np.random.rand(len(input_batch_sent), 500)


def model_call_single(input_sent: str):
    logger.info("processing through model")
    return model_call_batch([input_sent])[0]
