
import os
from pathlib import Path

import uvicorn
from decouple import config
from easyocr import Reader
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.openapi.utils import get_openapi
from models import get_unprocessed_ocr_frame_url
from ocr import (basic_post_processing, bolb_based_post_processing,
                 easyocr_read, main_ocr, word_base_post_processing)

base_path = os.path.dirname(os.path.abspath(__file__))




app = FastAPI()

if not config('DOCKER_ENABLE', cast=bool):
    print('running from gpu')
    langs = ['en']
    reader = Reader(langs, gpu=True)
else:
    langs = ['en']
    reader = Reader(langs)


@app.post("/local", status_code=200)
async def get_local_text(image_path: str):

    # print('----------------->', image_path)

    if not image_path or len(image_path.strip()) == 0:
        raise HTTPException(status_code=404, detail="image path is invalid or empty")
    else:
        main_file_path = os.path.realpath(os.path.basename(r'%s' % image_path))
        if not os.path.exists(main_file_path):
            raise HTTPException(status_code=404,
                                detail="image path is invalid / local file not found")
        try:
            simple_ouput_text = easyocr_read(main_file_path, reader)
            if len(simple_ouput_text) > 0:
                pass
            else:
                raise HTTPException(status_code=404,
                                    detail="text on an image not found")
        except FileNotFoundError:
            raise HTTPException(status_code=404,
                                detail="image path is invalid / local file not found")


        # post correction
        basic_correction = basic_post_processing(simple_ouput_text)
        blob_based_correction = bolb_based_post_processing(simple_ouput_text)
        word_based_correction = word_base_post_processing(simple_ouput_text)

        # Deep stack scene discription
        # deepstack_text = deepstack_image_discription(image_path)
        return {
            'image_text': simple_ouput_text,
            'basic_correction': basic_correction,
            'blob_based_correction': blob_based_correction,
            'word_based_correction': word_based_correction,
            'file_name': Path(image_path).name,
        }

@app.post("/online")
async def get_online_text(background_tasks: BackgroundTasks, request: Request):
    response = await request.json()
    # image_path = response['image_url']
    video_id = response['video_id']
    frame_id = response['frame_id']
    data = {'id':frame_id, 'video_id':video_id}
    image_path = await get_unprocessed_ocr_frame_url(data)
    try:
        if not image_path or len(image_path.strip()) == 0:
            raise HTTPException(status_code=400, detail="image path is invalid or empty")
        else:
            background_tasks.add_task(main_ocr, image_path, frame_id, video_id)

            return {
                'response': 'soon the predictions will be compeleted',
                'file_name': image_path,
            }
    except Exception as e:
        print('image not processed for some reason', e)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Point Duty - OCR API",
        version="V-0.0.0",
        description="The realtime image OCR api",
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
