import os
import sys
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, status
from fastapi.responses import ORJSONResponse
from loguru import logger
from pydantic import BaseModel

from model_call import model_call_single, model_call_batch
from redis_code_pub_sub import RedisPubSub

logger.remove()  # Remove the default logger
logger.add(sys.stdout, colorize=False, backtrace=True, diagnose=True)
if not os.getenv("REDIS_URL"):
    load_dotenv()

app = FastAPI()


class InputVal(BaseModel):
    input: str


class InputValBatch(BaseModel):
    input: List[str]


@app.post("/api/sentence-to-vector/single")
async def call_model_call_single(input_val: InputVal):
    try:
        rez = model_call_single(input_val.input)
        return ORJSONResponse(content={"val": rez, "error": None}, status_code=status.HTTP_202_ACCEPTED)
    except Exception as e:
        logger.error(e)
        return ORJSONResponse(content={"val": None, "error": e}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/api/sentence-to-vector/sync/batch")
async def call_model_call_batch(input_val: InputValBatch):
    try:
        rez = model_call_batch(input_val.input)
        return ORJSONResponse(content={"val": rez, "error": None}, status_code=status.HTTP_202_ACCEPTED)
    except Exception as e:
        logger.error(e)
        return ORJSONResponse(content={"val": [], "error": e}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/api/sentence-to-vector/async/batch")
async def push_work_on_worker(input_val: InputValBatch):
    try:
        redis_class_obj = RedisPubSub(host=os.getenv("REDIS_URL"))
        redis_class_obj.publish("channel_batman", {
            "message": input_val.input
        })
        return ORJSONResponse(content={"error": None}, status_code=status.HTTP_202_ACCEPTED)
    except Exception as e:
        logger.error(e)
        return ORJSONResponse(content={"error": e}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get("/api/sentence-to-vector/async/batch")
async def pull_from_processed_result(input_val: str):
    try:
        redis_class_obj = RedisPubSub(host=os.getenv("REDIS_URL"))
        rez = redis_class_obj.pull(input_val)
        return ORJSONResponse(content={"val": rez, "error": None}, status_code=status.HTTP_202_ACCEPTED)
    except Exception as e:
        logger.error(e)
        return ORJSONResponse(content={"val": None, "error": e}, status_code=status.HTTP_400_BAD_REQUEST)
