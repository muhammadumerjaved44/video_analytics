import asyncio
import ntpath
import os
from pathlib import Path

import cv2
import numpy as np
import requests
import torch
import uvicorn
from decouple import config
from detectron import pd_detectron2
from fastapi import Depends, FastAPI, Header, HTTPException, Response, BackgroundTasks
from fastapi.openapi.utils import get_openapi

# from settings import Settings, get_settings


base_path = os.path.dirname(os.path.abspath(__file__))


app = FastAPI()

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

@app.get("/online")
async def get_classes(background_tasks: BackgroundTasks, image_path: str):


    try:
        hdr = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(image_path, headers=hdr)
        if response.status_code != 200:
            pass
            print('error on response')
            return {'status': response.status_code}
        else:
            print('all good')
            # img = await url_to_image(response)
            # image = np.asarray(bytearray(response.content), dtype="uint8")
            # img = cv2.imdecode(image, cv2.IMREAD_COLOR)
    except:
        return {'massage': 'invalid image format in URL'}


    if not image_path:
        return {'massage': 'No text found on image'}
    else:
        # predictions = await main(im[0])
        # predictions = await asyncio.gather(
        #     asyncio.create_task(
        #         pd_detectron2(img)
        #         )
        #     )
        # print(predictions)
        # predictions = pd_detectron2(img)


        return {
            'response': 'predictions',
            'file_name': Path(image_path).name,
        }

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