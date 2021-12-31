import asyncio
import concurrent.futures
import json
import ntpath
import os
import pathlib
import shutil
import time
from typing import List, Optional

import uvicorn
import wget
from decouple import config
from fastapi import (
    BackgroundTasks,
    FastAPI,
    File,
    HTTPException,
    Path,
    Query,
    UploadFile,
)
from fastapi.openapi.utils import get_openapi

from frames import video_to_frames
from helper import snake_case
from models import (
    check_any_videos_left,
    check_in_progress_videos,
    get_unprocessed_videos_urls,
    get_videos,
    insert_video,
    upload_video,
)

base_path = os.path.dirname(os.path.abspath(__file__))


app = FastAPI()

ip_address = config("MY_IP")

list_of_moderation = [
    "porn_moderation",
    "suggestive_nudity_moderation",
    "gore_moderation",
    "money_moderation",
    "weapon_moderation",
    "drug_moderation",
    "hate_sign_moderation",
    "obscene_gesture_moderation",
    "qr_code_moderation",
    "face_detection",
    "face_age_detection",
    "face_gender_detection",
    "face_gender_age_detection",
    "content_moderation_profile",
]


@app.post("/local_decord", status_code=200, tags=["decord"])
async def get_decord_frames_local(
    background_tasks: BackgroundTasks,
    video_path: str = None,
    overwrite: bool = False,
    every: int = 1,
):

    dir_name = "./video_download/"
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    file_name = Path(video_path).name + ".mp4"
    full_path = dir_name + file_name
    print(full_path)
    if not os.path.exists(full_path):
        print("downloading video on server")
        try:
            wget.download(video_path, full_path)
        except:
            raise HTTPException(
                status_code=404, detail="link not working on server or expire"
            )

    video_path = video_path.strip()
    if not video_path or len(video_path) == 0:
        raise HTTPException(
            status_code=404, detail="video file path is invalid or empty"
        )
    else:
        # late we use minio folder to download videos
        main_file_path = os.path.realpath(
            "video_download/" + ntpath.basename(r"%s" % video_path)
        )
        if not os.path.exists(main_file_path):
            raise HTTPException(
                status_code=404,
                detail="video file path is invalid / local file not found",
            )
        try:
            background_tasks.add_task(video_to_frames, video_path, overwrite, every)

        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail="video file path is invalid / local file not found",
            )

        return {
            "response": "soon the video will be processed",
            "file_name": Path(main_file_path).name,
        }


@app.get("/online_decord", tags=["decord"])
async def get_decord_frames_online(
    background_tasks: BackgroundTasks, video_id, overwrite: bool = False, every: int = 1
):
    # video_path = video_path.strip()
    data = {"id": video_id, "is_video_processed": 0}
    video_path = await get_unprocessed_videos_urls(data)
    print(video_path)

    # video_path ='https://file-examples-com.github.io/uploads/2017/04/file_example_MP4_1280_10MG.mp4'
    # late we use minio folder to download videos
    # TODO:
    # 1) need to fix the path issues for video location
    # 2) delete the video from local folder if downloaded

    dir_name = "./video_download/"
    os.makedirs(os.path.join(dir_name), exist_ok=True)
    file_name = Path(video_path).name + ".mp4"
    full_path = dir_name + file_name
    print(full_path)
    if not os.path.exists(full_path):
        print("downloading video on server")
        try:
            wget.download(video_path, full_path)
        except:
            raise HTTPException(
                status_code=404, detail="link not working on server or expire"
            )
    try:
        background_tasks.add_task(
            video_to_frames, video_path, video_id, overwrite, every
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail="video file path is invalid / local file not found"
        )

    return {
        "response": "soon the video will be processed",
        "file_name": video_path,
    }


async def process_frames(paylaod, video_id, every):
    print("start new processing")
    try:
        await video_to_frames(paylaod, video_id, every)
    except:
        return {"status": 422}


def between_callback(paylaod, video_id, every):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(process_frames(paylaod, video_id, every))
        loop.close()
    except:
        return {"status": 422}


async def check_files_validity(video_file_list):
    list_of_extentions = [
        ".webm",
        ".mkv",
        ".flv",
        ".vob",
        ".ogv",
        ".ogg",
        ".mpg",
        ".mp2",
        ".mpeg",
        ".mpe",
        ".mpv",
        ".3gp",
        ".mp4",
        ".m4p",
        ".m4v",
        ".flv",
    ]

    for video_file in video_file_list:
        extention = pathlib.Path(video_file.filename).suffix
        if extention not in list_of_extentions:
            raise HTTPException(status_code=415, detail="Unsupported Media Type")


async def copyfile_into_local_folder(video_file_list, dir_name):

    file_location_list = []
    for video_file in video_file_list:
        file_name = await snake_case(video_file.filename)
        file_location = os.path.join(base_path, dir_name, str(file_name))
        file_location_list.append(file_location)
        print("\n\n\n\n", file_location)
        with open(file_location, mode="wb+") as file_object:
            shutil.copyfileobj(video_file.file, file_object)
    return file_location_list


@app.post("/upload_decord_files", tags=["Uplaod decord"])
async def upload_decord_files_and_get_frames(
    skip_frame: int,
    video_file_list: List[UploadFile] = File(...),
    is_ocr: bool = Query(
        False,
        choices=(True, False),
        description="is OCR service is required - by default False",
    ),
    is_detectron: bool = Query(
        False,
        choices=(True, False),
        description="is Detectron service is required - by default False",
    ),
    is_qr: bool = Query(
        False,
        choices=(True, False),
        description="is Qr Code service is required - by default False",
    ),
    is_picpurify: bool = Query(
        False,
        choices=(True, False),
        description="is Picpurify service is required - by default False",
    ),
    moderation: str = Query(
        "gore_moderation",
        enum=list_of_moderation,
        description="Select Picpurify service is required - by default gore_moderation",
    ),
):

    await check_files_validity(video_file_list)

    dir_name = "video_download"
    os.makedirs(os.path.join(dir_name), exist_ok=True)

    file_location_list = await copyfile_into_local_folder(video_file_list, dir_name)

    # print(is_ocr, is_detectron, is_picpurify, is_qr)

    for file_location in file_location_list:
        print("mian file path ", os.path.relpath(file_location))
        video_url, version_id = await upload_video(os.path.relpath(file_location))
        print("video url  ", video_url)

        data = {
            "video_name": os.path.basename(file_location),  # file base anme
            "version_id": version_id,
            "is_video_processed": 0,
            "is_in_progress": 0,
            "video_url": video_url,
        }

        print(data)
        await insert_video(data)

    is_progress = False
    is_any_video_left = True
    task = None

    paylaod = {
        "is_ocr": {"flag": is_ocr, "status": False},
        "is_detectron": {"flag": is_detectron, "status": False},
        "is_picpurify": {
            "flag": is_picpurify,
            "status": False,
            "moderation": moderation,
        },
        "is_qr": {"flag": is_qr, "status": False},
    }

    while True:
        try:
            print("is_progress, is_any_video_left", is_progress, is_any_video_left)
            if is_any_video_left and not is_progress:
                videos_data = await get_videos()
                try:
                    print(videos_data[0]["id"])
                except:
                    break

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    task = executor.submit(
                        between_callback,
                        paylaod=paylaod,
                        video_id=videos_data[0]["id"],
                        every=skip_frame,
                    )
                    print(task.result())
                    print("\n\n\n\n\n")
                    task_result = task.result()

                time.sleep(10)

            elif not is_any_video_left:
                print("the no video is left")
                break
            elif is_progress:
                print("the video is already in progress")
                is_progress = await check_in_progress_videos()
                is_any_video_left = await check_any_videos_left()
                print(
                    "runn from elseif is_progress, is_any_video_left",
                    is_progress,
                    is_any_video_left,
                )
                time.sleep(30)
        except KeyboardInterrupt:
            break


tags_metadata = [
    {
        "name": "decord",
        "description": "This End point use the decord to exract the frames from any video",
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
    app.openapi_tags = tags_metadata
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    # $ uvicorn main:app --reload
    port = config("FASTAPI_LOCAL_PORT", cast=int)
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload="True")
