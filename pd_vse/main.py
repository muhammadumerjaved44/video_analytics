import asyncio
import json
import os
import time

import aiohttp
import httpx
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


# start = time.time()

ip_address = config('MY_IP')

@app.post("/ocr", status_code=200)
async def trigger_OcrAPI(background_tasks: BackgroundTasks, db: Session = Depends(get_db), ):
    results = await get_OCR_frames(db)
    # for r in results:
    #     print(r)

    start_time = time.time()

    api_end_point =  f'http://{ip_address}:8050/online'

    async def make_api_asyc_call():
        async with aiohttp.ClientSession(json_serialize=json.dumps) as session:
            for result in results[0:10]:
                video_id = result['video_id']
                frame_id = result['id']
                await session.post(api_end_point, json={'frame_id': frame_id,'video_id': video_id})
            # await asyncio.gather(*tasks)
    background_tasks.add_task(make_api_asyc_call)
    end_time = time.time()
    total_time = end_time-start_time
    # print(end_time-start_time)
    # return {'result': all_frames}
    return {'Total_time': total_time, 'massage': 'prediction is initiated'}

@app.post("/detectron2", status_code=200)
async def trigger_detectron2API(background_tasks: BackgroundTasks, db: Session = Depends(get_db), ):
    results = await get_frames(db)
    # for r in results:
    #     print(r)
    # return(resp)
    start_time = time.time()
    # # tasks = []
    api_end_point =  f'http://{ip_address}:8060/online'

    async def make_api_asyc_call():
        async with aiohttp.ClientSession(json_serialize=json.dumps) as session:
            for result in results[0:10]:
                video_id = result['video_id']
                frame_id = result['id']
                await session.post(api_end_point, json={'frame_id': frame_id, 'video_id': video_id})
            # await asyncio.gather(*tasks)
    background_tasks.add_task(make_api_asyc_call)
    end_time = time.time()
    total_time = end_time-start_time
    # print(end_time-start_time)
    # return {'result': all_frames}
    return {'Total_time': total_time, 'massage': 'prediction is initiated'}

@app.get("/frames", status_code=200)
async def trigger_framesAPI(video_path, background_tasks: BackgroundTasks, overwrite:bool=False, every:int=1):
    # video_path='video_download/sample_video.mp4'
    # overwrite=False
    # every=1
    url = f'http://{ip_address}:8070/local_decord?video_path={video_path}&overwrite={overwrite}&every={every}'

    start_time = time.time()

    async def make_api_asyc_call():
        async with aiohttp.ClientSession(json_serialize=json.dumps) as session:
                await session.post(url)
            # await asyncio.gather(*tasks)
    background_tasks.add_task(make_api_asyc_call)
    end_time = time.time()
    total_time = end_time-start_time

    return {'Total_time': total_time, 'values': (video_path, overwrite, every, url)}

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
