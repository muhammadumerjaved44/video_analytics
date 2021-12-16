import asyncio
import json
import os
import time

import aiohttp
import uvicorn
from decouple import config
from analysis import content
from fastapi import (BackgroundTasks,Depends, FastAPI, Query)
# from fastapi.encoders import jsonable_encoder
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import get_counts, get_frames, get_OCR_frames, get_predictions, get_picpurify_frames


base_path = os.path.dirname(os.path.abspath(__file__))


app = FastAPI()
class Inputs(BaseModel):
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
async def trigger_Ocr_API(background_tasks: BackgroundTasks, db: Session = Depends(get_db), ):
    results = await get_OCR_frames(db)
    # for r in results:
    #     print(r)

    print('total records fetched from db', len(results))

    start_time = time.time()

    api_end_point =  f'http://{ip_address}:8003/online'

    async def make_api_asyc_call():
        async with aiohttp.ClientSession(json_serialize=json.dumps) as session:
            for result in results:
                video_id = result['video_id']
                frame_id = result['id']
                await session.post(api_end_point, json={'frame_id': frame_id,'video_id': video_id})
        await session.close()
            # await asyncio.gather(*tasks)
    background_tasks.add_task(make_api_asyc_call)
    end_time = time.time()
    total_time = end_time-start_time
    # print(end_time-start_time)
    # return {'result': all_frames}
    return {'Total_time': total_time, 'massage': 'prediction is initiated'}

@app.post("/detectron2", status_code=200)
async def trigger_detectron_API(background_tasks: BackgroundTasks, db: Session = Depends(get_db), ):
    results = await get_frames(db)
    # for r in results:
    #     print(r)
    # return(resp)
    print('total records fetched from db', len(results))
    start_time = time.time()
    # # tasks = []
    api_end_point =  f'http://{ip_address}:8001/online'

    async def make_api_asyc_call():
        async with aiohttp.ClientSession(json_serialize=json.dumps) as session:
            for result in results:
                video_id = result['video_id']
                frame_id = result['id']
                await session.post(api_end_point, json={'frame_id': frame_id, 'video_id': video_id})
            # await asyncio.gather(*tasks)
        await session.close()
    background_tasks.add_task(make_api_asyc_call)
    end_time = time.time()
    total_time = end_time-start_time
    # print(end_time-start_time)
    # return {'result': all_frames}
    return {'Total_time': total_time, 'massage': 'prediction is initiated'}

@app.get("/frames", status_code=200)
async def trigger_frames_API(video_path, background_tasks: BackgroundTasks, overwrite:bool=False, every:int=1):
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
    all_frames_list = await get_frames(db)
    return {'response': all_frames_list}

@app.get("/all_predictions", status_code=200)
async def all_predictions(db: Session = Depends(get_db)):
    all_data = await get_predictions(db)
    return {'response': all_data}

@app.get("/all_predictions_counts", status_code=200)
async def all_predictions_counts(db: Session = Depends(get_db)):
    all_count = await get_counts(db)
    return {'response': all_count}


@app.get("/pic_purify_api", status_code=200, tags=["PicPurify API"])
async def pic_purify_api(background_tasks: BackgroundTasks,
                         moderation: str = Query("gore_moderation",
                                                 enum=['gore_moderation',
                                                       'money_moderation',
                                                       'weapon_moderation',
                                                       'drug_moderation',
                                                       'hate_sign_moderation',
                                                       'obscene_gesture_moderation',
                                                       'qr_code_moderation',
                                                       'content_moderation_profile',
                                                       'porn_moderation',
                                                       'suggestive_nudity_moderation',]
                                                 ),
                         db: Session = Depends(get_db)):

    results = await get_picpurify_frames(db)
    # for r in results:
    #     print(r)
    # return(resp)
    print('total records fetched from db', len(results))
    start_time = time.time()

    api_end_point =  f'http://{ip_address}:8004/pic_purify_api_frames'

    async def make_api_asyc_call():
        async with aiohttp.ClientSession(json_serialize=json.dumps) as session:
            for result in results[0:1]:
                video_id = result['video_id']
                frame_id = result['id']
                await session.post(api_end_point, json={'frame_id': frame_id, 'video_id': video_id, 'moderation': moderation})
            # await asyncio.gather(*tasks)
        await session.close()
    background_tasks.add_task(make_api_asyc_call)
    end_time = time.time()
    total_time = end_time-start_time
    # print(end_time-start_time)
    # return {'result': all_frames}
    return {'Total_time': total_time, 'massage': 'picpurify prediction is initiated'}



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
