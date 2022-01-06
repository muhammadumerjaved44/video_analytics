import asyncio
import json
import os
import time
from datetime import timedelta
from typing import List

import aiohttp
import requests
import uvicorn
from asgiref.sync import async_to_sync
from decouple import config
from fastapi import BackgroundTasks, Depends, FastAPI, Query

# from fastapi.encoders import jsonable_encoder
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from timeloop import Timeloop

from celery_worker import (
    task_run_detectron_service,
    task_run_ocr_service,
    task_run_picpurify_service,
    task_run_qr_service,
)
from database import SessionLocal, engine
from models import (
    check_in_progress_videos,
    get_detectron_frames,
    get_ocr_frames,
    get_picpurify_frames,
    get_qr_frames,
)

base_path = os.path.dirname(os.path.abspath(__file__))


app = FastAPI()

qr_task = Timeloop()
detectron_task = Timeloop()
picpurify_task = Timeloop()
ocr_task = Timeloop()

# counter for the faliure
count_ocr_tries = 0
count_detectron_tries = 0
count_picpurify_tries = 0
count_qr_tries = 0


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# start = time.time()

ip_address = config("MY_IP")


@app.post("/ocr", status_code=200, tags=["OCR API"])
async def trigger_ocr_API(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    results = await get_ocr_frames(db)
    # for r in results:
    #     print(r)

    print("total records fetched from db", len(results))

    start_time = time.time()

    api_end_point = f"http://{ip_address}:8003/online"

    async def make_api_asyc_call():
        async with aiohttp.ClientSession(json_serialize=json.dumps) as session:
            for result in results:
                video_id = result["video_id"]
                frame_id = result["id"]
                await session.post(api_end_point, json={"frame_id": frame_id, "video_id": video_id})
        await session.close()
        # await asyncio.gather(*tasks)

    background_tasks.add_task(make_api_asyc_call)
    end_time = time.time()
    total_time = end_time - start_time
    # print(end_time-start_time)
    # return {'result': all_frames}
    return {"Total_time": total_time, "massage": "prediction is initiated"}


@app.post("/detectron2", status_code=200, tags=["Detectron2 API"])
async def trigger_detectron_API(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    results = await get_detectron_frames(db)
    # for r in results:
    #     print(r)
    # return(resp)
    print("total records fetched from db", len(results))
    start_time = time.time()
    # # tasks = []
    api_end_point = f"http://{ip_address}:8001/online"

    async def make_api_asyc_call():
        async with aiohttp.ClientSession(json_serialize=json.dumps) as session:
            for result in results:
                video_id = result["video_id"]
                frame_id = result["id"]
                await session.post(api_end_point, json={"frame_id": frame_id, "video_id": video_id})
            # await asyncio.gather(*tasks)
        await session.close()

    background_tasks.add_task(make_api_asyc_call)
    end_time = time.time()
    total_time = end_time - start_time
    # print(end_time-start_time)
    # return {'result': all_frames}
    return {"Total_time": total_time, "massage": "prediction is initiated"}


@app.get("/frames", status_code=200, tags=["Decord Frame API"])
async def trigger_frames_API(
    video_path,
    background_tasks: BackgroundTasks,
    overwrite: bool = False,
    every: int = 1,
):
    # video_path='video_download/sample_video.mp4'
    # overwrite=False
    # every=1
    url = f"http://{ip_address}:8070/local_decord?video_path={video_path}&overwrite={overwrite}&every={every}"

    start_time = time.time()

    async def make_api_asyc_call():
        async with aiohttp.ClientSession(json_serialize=json.dumps) as session:
            await session.post(url)
            # await asyncio.gather(*tasks)

    background_tasks.add_task(make_api_asyc_call)
    end_time = time.time()
    total_time = end_time - start_time

    return {"Total_time": total_time, "values": (video_path, overwrite, every, url)}


@app.get("/pic_purify_api", status_code=200, tags=["PicPurify API"])
async def pic_purify_api(
    background_tasks: BackgroundTasks,
    moderation: str = Query(
        "gore_moderation",
        enum=[
            "gore_moderation",
            "money_moderation",
            "weapon_moderation",
            "drug_moderation",
            "hate_sign_moderation",
            "obscene_gesture_moderation",
            "qr_code_moderation",
            "content_moderation_profile",
            "porn_moderation",
            "suggestive_nudity_moderation",
        ],
    ),
    db: Session = Depends(get_db),
):

    results = await get_picpurify_frames(db)

    print("total records fetched from db", len(results))
    start_time = time.time()

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
                        "moderation": moderation,
                    },
                )
            # await asyncio.gather(*tasks)
        await session.close()

    background_tasks.add_task(make_api_asyc_call)
    end_time = time.time()
    total_time = end_time - start_time
    # print(end_time-start_time)
    # return {'result': all_frames}
    return {"Total_time": total_time, "massage": "picpurify prediction is initiated"}


@app.post("/perform_qr_code", status_code=200, tags=["Qr Code API"])
async def perform_qr_code(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    results = await get_qr_frames(db)
    # for r in results:
    #     print(r)
    # return(resp)
    print("total records fetched from db", len(results))
    start_time = time.time()
    # # tasks = []
    api_end_point = f"http://{ip_address}:8006/perform_qr_code_to_text"

    async def make_api_asyc_call():
        async with aiohttp.ClientSession(json_serialize=json.dumps) as session:
            for result in results:
                video_id = result["video_id"]
                frame_id = result["id"]
                await session.post(api_end_point, json={"frame_id": frame_id, "video_id": video_id})
            # await asyncio.gather(*tasks)
        await session.close()

    background_tasks.add_task(make_api_asyc_call)
    end_time = time.time()
    total_time = end_time - start_time
    # print(end_time-start_time)
    # return {'result': all_frames}
    return {"Total_time": total_time, "massage": "prediction is initiated"}


@app.post("/run_ocr_service", tags=["Worker"])
def run_ocr_service():
    global count_ocr_tries
    task = task_run_ocr_service.delay()
    while not task.ready():
        pass
    if task.get() == []:
        is_progress = async_to_sync(check_in_progress_videos)()
        if is_progress:
            time.sleep(60)
            count_ocr_tries = 0
        count_ocr_tries = count_ocr_tries + 1
        if count_ocr_tries == 2:
            ocr_task.stop()
            count_ocr_tries = 0
    return JSONResponse({"task_status": task.status, "resutls:": task.get(), "task_id": task.id})


@app.post("/run_detectron_service", tags=["Worker"])
def run_detectron_service():
    global count_detectron_tries
    task = task_run_detectron_service.delay()
    while not task.ready():
        pass
    if task.get() == []:
        is_progress = async_to_sync(check_in_progress_videos)()
        if is_progress:
            time.sleep(60)
            count_detectron_tries = 0
        count_detectron_tries = count_detectron_tries + 1
        if count_detectron_tries == 2:
            detectron_task.stop()
            count_detectron_tries = 0
    return JSONResponse({"task_status": task.status, "resutls:": task.get(), "task_id": task.id})


@app.post("/run_picpurify_service", tags=["Worker"])
def run_picpurify_service(moderation: dict):
    # data =request.query_params()
    global count_picpurify_tries
    moderation_type = moderation["moderation_type"]
    task = task_run_picpurify_service.delay(moderation_type)
    while not task.ready():
        pass
    if task.get() == []:
        is_progress = async_to_sync(check_in_progress_videos)()
        if is_progress:
            time.sleep(60)
            count_picpurify_tries = 0
        count_picpurify_tries = count_picpurify_tries + 1
        if count_picpurify_tries == 2:
            picpurify_task.stop()
            count_picpurify_tries = 0
    return JSONResponse({"task_status": task.status, "resutls:": task.get(), "task_id": task.id})


@app.post("/run_qr_service", tags=["Worker"])
def run_qr_service():
    global count_qr_tries
    task = task_run_qr_service.delay()
    while not task.ready():
        pass
    if task.get() == []:
        is_progress = async_to_sync(check_in_progress_videos)()
        if is_progress:
            time.sleep(60)
            count_qr_tries = 0
        count_qr_tries = count_qr_tries + 1
        if count_qr_tries == 2:
            qr_task.stop()
            count_qr_tries = 0
    return JSONResponse({"task_status": task.status, "resutls:": task.get(), "task_id": task.id})


@ocr_task.job(interval=timedelta(seconds=5))
def run_ocr_code():
    requests.post("http://192.168.20.200:8000/run_ocr_service")


@detectron_task.job(interval=timedelta(seconds=5))
def run_detectron_code():
    requests.post("http://192.168.20.200:8000/run_detectron_service")


@picpurify_task.job(interval=timedelta(seconds=5))
def run_qr_code():
    data = json.dumps({"moderation_type": moderation})
    requests.post("http://192.168.20.200:8000/run_picpurify_service", params=data)


@qr_task.job(interval=timedelta(seconds=5))
def run_qr_code():
    requests.post("http://192.168.20.200:8000/run_qr_service")


@app.get("/simple_massage_service", tags=["Worker Send massage"])
def send_massage(massage):
    msg = json.loads(massage)
    if msg["is_ocr"]["flag"] == True and msg["is_ocr"]["status"] == False:
        ocr_task.start()

    if msg["is_detectron"]["flag"] == True and msg["is_detectron"]["status"] == False:
        detectron_task.start()

    if msg["is_picpurify"]["flag"] == True and msg["is_picpurify"]["status"] == False:
        global moderation
        moderation = msg["is_picpurify"]["moderation"]
        picpurify_task.start()
    if msg["is_qr"]["flag"] == True and msg["is_qr"]["status"] == False:
        qr_task.start()
    else:
        print(msg)

    print(" [x] Recieved from Frames API 'Hello World!'", json.loads(massage))
    # connection.close()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Point Duty - Video Search Engine API",
        version="V-0.0.0",
        description="No description",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {"url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"}
    app.openapi_schema = openapi_schema
    # app.openapi_tags=tags_metadata
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == "__main__":
    # $ uvicorn main:app --reload
    port = config("FASTAPI_LOCAL_PORT", cast=int)
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload="True")
