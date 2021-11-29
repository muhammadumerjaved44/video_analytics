import os
from pathlib import Path
from typing import Optional

import requests
from easyocr import Reader
from fastapi import (BackgroundTasks, Depends, FastAPI, Header, HTTPException,
                     Request, Response)
import uvicorn
from PIL import Image
from textblob import TextBlob
from decouple import config
from fastapi.openapi.utils import get_openapi
from database import SessionLocal
from pathlib import Path

# import nltk
# # nltk.download('all')

base_path = os.path.dirname(os.path.abspath(__file__))



from ocr import (basic_post_processing, bolb_based_post_processing, easyocr_read,
                        word_base_post_processing, main_ocr)

app = FastAPI()
langs = ['en']
reader = Reader(langs)


@app.post("/local", status_code=200)
async def get_text(image_path: str, response: Response):

    # print('----------------->', image_path)

    if not image_path or len(image_path.strip()) == 0:
        # return {'massage': 'No text found on image'}
        raise HTTPException(status_code=404, detail="image path is invalid or empty")
    else:
        main_file_path = os.path.realpath(os.path.basename(r'%s' % image_path))
        if not os.path.exists(main_file_path):
            raise HTTPException(status_code=404, detail="image path is invalid / local file not found")
        try:
            simple_ouput_text = easyocr_read(main_file_path, reader)
            if len(simple_ouput_text) > 0:
                pass
            else:
                raise HTTPException(status_code=404, detail="text on an image not found")
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="image path is invalid / local file not found")


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
async def get_text(background_tasks: BackgroundTasks, request: Request):
    data = await request.json()
    image_path = data['image_url']
    try:
        if not image_path or len(image_path.strip()) == 0:
            raise HTTPException(status_code=404, detail="image path is invalid or empty")
        else:
            background_tasks.add_task(main_ocr, image_path)

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