import asyncio
import ntpath
import os
import threading
import time
from pathlib import Path

import uvicorn
import wget
from decouple import config
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from frames import video_to_frames
from models import (check_any_videos_left, check_in_progress_videos,
                    get_unprocessed_videos_urls, get_videos, insert_video,
                    upload_video)

base_path = os.path.dirname(os.path.abspath(__file__))


app = FastAPI()


@app.post("/local_decord", status_code=200, tags=["decord"])
async def get_decord_frames_local(background_tasks: BackgroundTasks,
                                  video_path:str = None,
                                  overwrite:bool =False,
                                  every: int = 1):

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
            raise HTTPException(status_code=404,
                                detail="link not working on server or expire")

    video_path = video_path.strip()
    if not video_path or len(video_path) == 0:
        raise HTTPException(status_code=404,
                            detail="video file path is invalid or empty")
    else:
        # late we use minio folder to download videos
        main_file_path = os.path.realpath('video_download/'+ntpath.basename(r'%s' % video_path))
        if not os.path.exists(main_file_path):
            raise HTTPException(status_code=404,
                                detail="video file path is invalid / local file not found")
        try:
            background_tasks.add_task(video_to_frames,video_path, overwrite, every)

        except FileNotFoundError:
            raise HTTPException(status_code=404,
                                detail="video file path is invalid / local file not found")

        return {
            'response': 'soon the video will be processed',
            'file_name': Path(main_file_path).name,
        }

@app.get("/online_decord", tags=["decord"])
async def get_decord_frames_online(background_tasks: BackgroundTasks,
                                   video_id,
                                   overwrite:bool =False,
                                   every: int = 1):
    # video_path = video_path.strip()
    data = {'id': video_id, 'is_video_processed': 0}
    video_path = await get_unprocessed_videos_urls(data)
    print(video_path)

    # video_path ='https://file-examples-com.github.io/uploads/2017/04/file_example_MP4_1280_10MG.mp4'
    # late we use minio folder to download videos
    #TODO:
    # 1) need to fix the path issues for video location
    # 2) delete the video from local folder if downloaded

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
            raise HTTPException(status_code=404,
                                detail="link not working on server or expire")
    try:
        background_tasks.add_task(video_to_frames, video_path, video_id, overwrite, every)
    except FileNotFoundError:
        raise HTTPException(status_code=404,
                            detail="video file path is invalid / local file not found")


    return {
        'response': 'soon the video will be processed',
        'file_name': video_path,
    }

async def process_frames(video_id, overwrite:bool =False , every: int = 1):
    print('start new processing')
    data = {'id': video_id}
    video_path = await get_unprocessed_videos_urls(data)
    print('my video path', video_path)

    await video_to_frames(video_path, video_id, overwrite, every)

def between_callback(video_id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(process_frames(video_id))
    loop.close()


@app.get("/upload_decord_files", tags=["decord"])
async def upload_decord_files_and_get_frames(file_path):
    dir_name = './video_download/'
    os.makedirs(os.path.join(dir_name), exist_ok=True)
    full_path = file_path
    main_file_path = os.path.realpath('video_download/'+ntpath.basename(r'%s' % full_path))
    print(main_file_path)
    try:
        if not os.path.exists(main_file_path):
            print('downloading video on server')
            wget.download(file_path, main_file_path)
    except Exception as e:
        print('file not properly downloaded', e)

    print('mian file path ', os.path.relpath(main_file_path))
    video_url, version_id = await upload_video(os.path.relpath(main_file_path))
    print('video url  ', video_url)

    data = {"video_name": Path(main_file_path).name,
            'version_id': version_id,
            'is_video_processed': 0,
            'is_in_progress':0,
            'video_url': video_url,
            }

    print(data)
    await insert_video(data)


    is_progress = False
    is_any_video_left = True
    while True:
        try:
            print('is_progress, is_any_video_left', is_progress, is_any_video_left)
            if is_any_video_left and not is_progress:
                videos_data = await get_videos()
                try:
                    print(videos_data[0]['id'])
                except:
                    break
                thread_1 = threading.Thread(target=between_callback, kwargs={'video_id': videos_data[0]['id']})
                print('start new thread', thread_1.name)
                thread_1.start()
                thread_1.join()
            elif not is_any_video_left:
                print('the no video is left')
                break
            elif is_progress:
                print('the video is already in progress')
                is_progress  = await check_in_progress_videos()
                is_any_video_left = await check_any_videos_left()
                print('runn from elseif is_progress, is_any_video_left', is_progress, is_any_video_left)
                time.sleep(30)
        except KeyboardInterrupt:
            break



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
