import os

import uvicorn
from decouple import config
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, Query
from fastapi.openapi.utils import get_openapi

from models import get_unprocessed_picpurify_frame_url
from picpurify import perform_picpurify

base_path = os.path.dirname(os.path.abspath(__file__))


app = FastAPI()

@app.post("/pic_purify_api_frames", status_code=200, tags=["PicPurify API"])
async def pic_purify_api_frames(background_tasks: BackgroundTasks,request: Request):

    # if request.method == 'POST':
    data = await request.json()
    print(data)
    print('this is post reqest')

    video_id = data['video_id']
    frame_id = data['frame_id']
    moderation  = data['moderation']

    input_data = {'id':frame_id, 'video_id':video_id}
    image_path = await get_unprocessed_picpurify_frame_url(input_data)

    try:
        if not image_path or len(image_path.strip()) == 0:
            raise HTTPException(status_code=404, detail="image path is invalid or empty")
        else:
            background_tasks.add_task(perform_picpurify, image_path, frame_id, video_id, moderation)

            return {
                'response': 'soon the predictions will be compeleted',
                'file_name': image_path,
            }
    except:
        print('image not processed for some reason')
    # print({'image_path': image_path, 'video_id': video_id, 'frame_id':frame_id, 'moderation':moderation })
    return {'image_path': image_path, 'video_id': video_id, 'frame_id':frame_id, 'moderation':moderation }


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Point Duty - Pic Purify API",
        version="V-0.0.0",
        description="The RealTime Modration Checking api",
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
