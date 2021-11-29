import asyncio
import json
import os
import time

import aiohttp
import httpx
import numpy as np
import requests
import uvicorn
from decouple import config
from fastapi import (BackgroundTasks, Body, Depends, FastAPI, HTTPException,
                     Request, Response)
# from fastapi.encoders import jsonable_encoder
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import get_counts, get_frames, get_OCR_frames, get_predictions

base_path = os.path.dirname(os.path.abspath(__file__))


app = FastAPI()
class inputs(BaseModel):
    image_url:str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def my_calls(url):
    resp = requests.get(url)
    resp = resp.json()
    return resp

async def my_post_frames_calls(url):
    # data.image_url = image_url
    resp = requests.post(url)
    resp = resp.json()
    # print(resp)
    return resp

async def my_post_calls(image_url):
    # data.image_url = image_url
    resp = requests.post('http://192.168.20.200:8060/online', json.dumps({"image_url":image_url}))
    resp = resp.json()
    # print(resp)
    return resp

# start = time.time()

my_ip = config('MY_IP')

@app.post("/ocr", status_code=200)
async def trigger_OcrAPI(background_tasks: BackgroundTasks, db: Session = Depends(get_db), ):
    results = await get_OCR_frames(db)
    # print(results)
    # return(resp)
    start_time = time.time()
    # # tasks = []
    for i in results:
        print(i[3])
        # data.image_url = i[3]
    # url = f'http://192.168.20.200:8060/online?image_path={image_url}'
        payload = json.dumps({"image_url":i[3]})
        resp = requests.post(f'http://{my_ip}:8050/online', payload)
        resp = resp.json()
        # background_tasks.add_task(my_post_calls, i[3])

    end_time = time.time()
    total_time = end_time-start_time
    # print(end_time-start_time)
    # return {'result': all_frames}
    return {'Total_time': total_time, 'massage': 'prediction is initiated'}

@app.post("/detectron2", status_code=200)
async def trigger_detectron2API(background_tasks: BackgroundTasks, db: Session = Depends(get_db), ):
    results = await get_frames(db)
    # print(results)
    # return(resp)
    start_time = time.time()
    # # tasks = []
    for i in results:
        print(i[3])
        # data.image_url = i[3]
    # url = f'http://192.168.20.200:8060/online?image_path={image_url}'
        payload = json.dumps({"image_url":i[3]})
        resp = requests.post(f'http://{my_ip}:8060/online', payload)
        resp = resp.json()
        # background_tasks.add_task(my_post_calls, i[3])

    end_time = time.time()
    total_time = end_time-start_time
    # print(end_time-start_time)
    # return {'result': all_frames}
    return {'Total_time': total_time, 'massage': 'prediction is initiated'}

@app.get("/frames", status_code=200)
async def trigger_framesAPI(video_path, frames_dir, background_tasks: BackgroundTasks, overwrite:bool=False, every:int=1):
    start_time = time.time()
    url = f'http://{my_ip}:8070/local_decord?video_path={video_path}&frames_dir={frames_dir}&overwrite={overwrite}&every={every}'
    print(url)
    background_tasks.add_task(my_post_frames_calls, url)
    end_time = time.time()
    total_time = end_time-start_time
    print(total_time)

    return {'Total_time': total_time, 'values': (video_path, frames_dir, overwrite, every, url)}

@app.get("/all_frames", status_code=200)
async def all_frames(db: Session = Depends(get_db)):
    all_frames = await get_frames(db)
    return {'response': all_frames}

@app.get("/all_predictions", status_code=200)
async def all_predictions(db: Session = Depends(get_db)):
    all_data = await get_predictions(db)
    return {'response': all_data}

@app.get("/all_predictions_counts", status_code=200)
async def all_predictions_counts(db: Session = Depends(get_db)):
    all_count = await get_counts(db)
    return {'response': all_count}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Point Duty - Video Search Engine API",
        version="V-0.0.0",
        description="No description",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    # app.openapi_tags=tags_metadata
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == "__main__":
    # $ uvicorn main:app --reload
    port = config('FASTAPI_LOCAL_PORT', cast=int)
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload="True")
