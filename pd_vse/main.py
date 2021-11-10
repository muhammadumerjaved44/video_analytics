import asyncio
import json
import multiprocessing
import ntpath
import os
import signal
import sys
import time
from multiprocessing import Pool, cpu_count
from pathlib import Path

import aiohttp
import httpx
import models as mod
import numpy as np
import requests
import uvicorn
from database import SessionLocal, engine
from decouple import config
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Response
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session

# from models import get_frames, get_predictions, get_counts

base_path = os.path.dirname(os.path.abspath(__file__))


app = FastAPI()

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

async def my_post_calls(url):
    resp = requests.post(url)
    resp = resp.json()
    return resp

# start = time.time()

@app.get("/detectron2", status_code=200)
async def trigger_detectron2API(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):

    results = await mod.get_frames(db)

    start_time = time.time()
    # tasks = []
    for i in results:
        # print(i)
        url = f'http://192.168.20.200:8060/local?image_path={i[3]}'
        background_tasks.add_task(my_calls, url)

    end_time = time.time()
    total_time = end_time-start_time
    print(end_time-start_time)

    return {'Total_time': total_time, 'massage': 'prediction is initiated'}

@app.get("/frames", status_code=200)
async def trigger_framesAPI(video_path, frames_dir, background_tasks: BackgroundTasks, overwrite:bool=False, every:int=1):
    start_time = time.time()
    url = f'http://192.168.20.200:8070/local_decord?video_path={video_path}&frames_dir={frames_dir}&overwrite={overwrite}&every={every}'
    print(url)
    background_tasks.add_task(my_post_calls, url)
    end_time = time.time()
    total_time = end_time-start_time
    print(total_time)

    return {'Total_time': total_time, 'values': (video_path, frames_dir, overwrite, every, url)}

@app.get("/all_frames", status_code=200)
async def all_frames(db: Session = Depends(get_db)):
    all_frames = await mod.get_frames(db)
    return {'response': all_frames}

@app.get("/all_predictions", status_code=200)
async def all_predictions(db: Session = Depends(get_db)):
    all_data = await mod.get_predictions(db)
    return {'response': all_data}

@app.get("/all_predictions_counts", status_code=200)
async def all_predictions_counts(db: Session = Depends(get_db)):
    all_count = await mod.get_counts(db)
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