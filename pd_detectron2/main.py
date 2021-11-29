import ntpath
import os
from pathlib import Path

import uvicorn
from decouple import config
from fastapi import (BackgroundTasks, Depends, FastAPI, Header, HTTPException,
                     Request, Response)
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel

from detectron import pd_detectron2, pd_detectron2_cloud
from models import get_unprocessed_frame_url

# from settings import Settings, get_settings


base_path = os.path.dirname(os.path.abspath(__file__))


app = FastAPI()

@app.get("/server", status_code=200)
async def get_classes(image_path, background_tasks: BackgroundTasks):
    # verify_auth(authorization, settings)
    if not image_path or len(image_path.strip()) == 0:
        raise HTTPException(status_code=404, detail="image path is invalid or empty")
    else:
        main_file_path = os.path.realpath(image_path)
        if not os.path.exists(main_file_path):
            raise HTTPException(status_code=404, detail="image path is invalid / local file not found")
        try:
            background_tasks.add_task(pd_detectron2, main_file_path)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="image path is invalid / local file not found")

        return {
            'response': 'soon the predictions will be compeleted',
            'file_name': Path(main_file_path).name,
        }

@app.get("/local", status_code=200)
async def get_classes(image_path, background_tasks: BackgroundTasks):
    # verify_auth(authorization, settings)
    if not image_path or len(image_path.strip()) == 0:
        raise HTTPException(status_code=404, detail="image path is invalid or empty")
    else:
        main_file_path = os.path.realpath(ntpath.basename(r'%s' % image_path))
        if not os.path.exists(main_file_path):
            raise HTTPException(status_code=404, detail="image path is invalid / local file not found")
        try:
            background_tasks.add_task(pd_detectron2, main_file_path)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="image path is invalid / local file not found")

        return {
            'response': 'soon the predictions will be compeleted',
            'file_name': Path(main_file_path).name,
        }


@app.post("/online")
async def get_classes(background_tasks: BackgroundTasks, request: Request):
    data = await request.json()
    # image_path = data['image_url']
    video_id = data['video_id']
    frame_id = data['frame_id']
    input_data = {'id':frame_id, 'video_id':video_id}
    image_path = await get_unprocessed_frame_url(input_data)
    try:
        if not image_path or len(image_path.strip()) == 0:
            raise HTTPException(status_code=404, detail="image path is invalid or empty")
        else:
            background_tasks.add_task(pd_detectron2_cloud, image_path,frame_id, video_id)

            return {
                'response': 'soon the predictions will be compeleted',
                'file_name': image_path,
            }
    except:
        print('image not processed for some reason')

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Point Duty - Detectron2 API",
        version="V-0.0.0",
        description="The RealTime Detectron api",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    # $ uvicorn main:app --reload
    port = config('FASTAPI_LOCAL_PORT', cast=int)
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload="True")
