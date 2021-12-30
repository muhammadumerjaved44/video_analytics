import asyncio
import datetime
import json
import os
import time
from threading import Lock

import aiohttp
from asgiref.sync import async_to_sync
from celery import Celery
from celery.schedules import crontab
from database import SessionLocal, engine
from decouple import config
from fastapi import BackgroundTasks, Depends
from models import (
    get_detectron_frames,
    get_ocr_frames,
    get_picpurify_frames,
    get_qr_frames,
)
from sqlalchemy.orm import Session

celery = Celery(__name__)
celery.conf.broker_url = config("CELERY_BROKER_URL")
celery.conf.result_backend = config("CELERY_RESULT_BACKEND")
celery.conf.accept_content = ["json"]
celery.autodiscover_tasks()

# celery.conf.beat_schedule = {
#     "run-me-every-ten-seconds": {
#         "task": "task_run_qr_service",
#         "schedule": 10.0
#         },
#     "run-detectron-every-ten-seconds": {
#         "task": "task_run_detectron_service",
#         "schedule": 10.0
#         }
# }

ip_address = config("MY_IP")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# callback fucntion for OCR service
async def call_back_ocr():
    db = SessionLocal()
    results = await get_ocr_frames(db)

    api_end_point = f"http://{ip_address}:8003/online"

    async def make_api_asyc_call():
        async with aiohttp.ClientSession(json_serialize=json.dumps) as session:
            for result in results[0:10]:
                video_id = result["video_id"]
                frame_id = result["id"]
                await session.post(
                    api_end_point, json={"frame_id": frame_id, "video_id": video_id}
                )
        await session.close()

    await make_api_asyc_call()
    return results


# callback fucntion for Detectron service
async def call_back_detectron():
    db = SessionLocal()
    results = await get_detectron_frames(db)

    api_end_point = f"http://{ip_address}:8001/online"

    async def make_api_asyc_call():
        async with aiohttp.ClientSession(json_serialize=json.dumps) as session:
            for result in results[0:10]:
                video_id = result["video_id"]
                frame_id = result["id"]
                await session.post(
                    api_end_point, json={"frame_id": frame_id, "video_id": video_id}
                )
        await session.close()

    await make_api_asyc_call()
    return results


# callback fucntion for PicPurify service
async def call_back_picpurify(moderation_type):
    db = SessionLocal()
    results = await get_picpurify_frames(db)

    api_end_point = f"http://{ip_address}:8004/pic_purify_api_frames"

    async def make_api_asyc_call():
        async with aiohttp.ClientSession(json_serialize=json.dumps) as session:
            for result in results[0:1]:
                video_id = result["video_id"]
                frame_id = result["id"]
                await session.post(
                    api_end_point,
                    json={
                        "frame_id": frame_id,
                        "video_id": video_id,
                        "moderation": moderation_type,
                    },
                )
        await session.close()

    await make_api_asyc_call()
    return results


# callback fucntion for QR Code service
async def call_back_qrcode():
    db = SessionLocal()
    results = await get_qr_frames(db)
    api_end_point = f"http://{ip_address}:8006/perform_qr_code_to_text"

    async def make_api_asyc_call():
        async with aiohttp.ClientSession(json_serialize=json.dumps) as session:
            for result in results[0:5]:
                video_id = result["video_id"]
                frame_id = result["id"]
                await session.post(
                    api_end_point, json={"frame_id": frame_id, "video_id": video_id}
                )
        await session.close()

    await make_api_asyc_call()
    return results


@celery.task(name="task_run_ocr_service")
def task_run_ocr_service():
    result = async_to_sync(call_back_ocr)()
    return result


@celery.task(name="task_run_detectron_service")
def task_run_detectron_service():
    result = async_to_sync(call_back_detectron)()
    return result


@celery.task(name="task_run_picpurify_service")
def task_run_picpurify_service(moderation_type):
    result = async_to_sync(call_back_picpurify)(moderation_type)
    return result


@celery.task(name="task_run_qr_service")
def task_run_qr_service():
    result = async_to_sync(call_back_qrcode)()
    return result
