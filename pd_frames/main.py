import ntpath
import os
from pathlib import Path

import uvicorn
import wget
from decouple import config
from fastapi import BackgroundTasks, FastAPI, HTTPException, UploadFile, File
from fastapi.openapi.utils import get_openapi
from frames import video_to_frames
from typing import List
from decouple import config
from models import upload_video, insert_video

base_path = os.path.dirname(os.path.abspath(__file__))


app = FastAPI()


@app.post("/local_decord", status_code=200, tags=["decord"])
async def get_frames(background_tasks: BackgroundTasks, video_path:str = None, overwrite:bool =False , every: int = 1):

    dir_name = './video_download/'
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    file_name = Path(video_path).name+'.mp4'
    full_path = dir_name+file_name
    print(full_path)
    if not os.path.exists(full_path):
        print('downloading video on server')
        try:
            wget.download(video_path, full_path)
        except:
            raise HTTPException(status_code=404, detail="link not working on server or expire")

    video_path = video_path.strip()
    if not video_path or len(video_path) == 0:
        raise HTTPException(status_code=404, detail="video file path is invalid or empty")
    else:
        # late we use minio folder to download videos
        main_file_path = os.path.realpath('video_download/'+ntpath.basename(r'%s' % video_path))
        if not os.path.exists(main_file_path):
            raise HTTPException(status_code=404, detail="video file path is invalid / local file not found")
        try:
            background_tasks.add_task(video_to_frames,video_path, overwrite, every)

        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="video file path is invalid / local file not found")

        return {
            'response': 'soon the video will be processed',
            'file_name': Path(main_file_path).name,
        }

@app.get("/online_decord", tags=["decord"])
async def get_frames(background_tasks: BackgroundTasks,
                     video_path=None, overwrite:bool =False , every: int = 1):
    video_path = video_path.strip()

    # video_path ='https://file-examples-com.github.io/uploads/2017/04/file_example_MP4_1280_10MG.mp4'
    # late we use minio folder to download videos
    # todo: need to fix the path issues for video location

    dir_name = './video_download/'
    os.makedirs(os.path.join(dir_name), exist_ok=True)
    file_name = Path(video_path).name+'.mp4'
    full_path = dir_name+file_name
    print(full_path)
    if not os.path.exists(full_path):
        print('downloading video on server')
        try:
            wget.download(video_path, full_path)
        except:
            raise HTTPException(status_code=404, detail="link not working on server or expire")
    try:
        background_tasks.add_task(video_to_frames,video_path, overwrite, every)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="video file path is invalid / local file not found")


    return {
        'response': 'soon the video will be processed',
        'file_name': file_name,
    }


@app.get("/upload_decord_files", tags=["decord"])
async def get_frames(background_tasks: BackgroundTasks, file_path):
    dir_name = './video_download/'
    os.makedirs(os.path.join(dir_name), exist_ok=True)
    full_path = file_path
    main_file_path = os.path.realpath('video_download/'+ntpath.basename(r'%s' % full_path))
    print(main_file_path)
    if not os.path.exists(main_file_path):
        print('downloading video on server')
        try:
            wget.download(file_path, main_file_path)
        except:
            print('file already there')

    print('umer ', os.path.relpath(main_file_path))
    video_url = await upload_video(os.path.relpath(main_file_path))
    print('umer  ', video_url)
    data = {"video_name": Path(main_file_path).name, 'video_url': video_url, 'is_video_processed': 0}
    await insert_video(data)
    # return {"filenames": [file.filename for file in files], 'file_stream_size': [file.content_type for file in files]}



tags_metadata = [
    {
        "name": "decord",
        "description": 'This End point use the decord to exract the frames from any video',
    }
]

description = """
Frame Extraction API 🚀

## Online Video URL

<a href="https://file-examples-com.github.io/uploads/2017/04/file_example_MP4_1280_10MG.mp4" target="_blank">https://file-examples-com.github.io/uploads/2017/04/file_example_MP4_1280_10MG.mp4</a>

"""

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Point Duty - Frame Extraction API - Decord",
        version="V-0.0.0",
        description=description,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    app.openapi_tags=tags_metadata
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    # $ uvicorn main:app --reload
    port = config('FASTAPI_LOCAL_PORT', cast=int)
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload="True")