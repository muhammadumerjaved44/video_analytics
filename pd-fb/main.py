import asyncio
import concurrent.futures
import glob
import io
import os
import random
import string
import time
from pathlib import Path
from typing import List, Optional

import requests
import uvicorn
from decouple import config
from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.openapi.utils import get_openapi

from models import (
    check_any_videos_left,
    check_in_progress_videos,
    get_profiles,
    insert_video,
)
from scraper import main

app = FastAPI()

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


def random_string(N=24) -> str:
    """genrate random name for file saving

    Args:
        N (int, optional): random string length. Defaults to 6.

    Returns:
        str: resturn 6 letters random string
    """

    return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))


async def process_profiles(paylaod, video_id, video_name):
    print("start new processing")
    try:
        await main(paylaod, video_id, video_name)
    except:
        return {"status": 422}


def between_callback(paylaod, video_id, video_name):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(process_profiles(paylaod, video_id, video_name))
        loop.close()
    except:
        return {"status": 422}


@app.post("/scrap", tags=["demo"])
async def get_profile_images(
    profile_name_list: List[str] = Query(
        "alfred.lua",
        description="add profile id e.g alfred.lua or 100012359381139",
    ),
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

    # profiles uploaded
    for profile_name in profile_name_list:
        # print("mian file path ", os.path.relpath(profile_name))
        if profile_name.isdigit():
            profile_url = f"https://www.facebook.com/profile.php?id={profile_name}"
        else:
            profile_url = f"https://www.facebook.com/{profile_name}"
        data = {
            "video_name": str(profile_name),  # file base anme
            "version_id": random_string(),
            "is_video_processed": 0,
            "is_in_progress": 0,
            "video_url": profile_url,
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
                profile_data = await get_profiles()
                try:
                    print(profile_data[0]["id"])
                except:
                    break

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    task = executor.submit(
                        between_callback,
                        paylaod=paylaod,
                        video_id=profile_data[0]["id"],
                        video_name=profile_data[0]["video_name"],
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


def custom_openapi():

    if app.openapi_schema:

        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Point Duty - Facebook Scraper API",
        version="V-0.0.0",
        description="The Facebook Scraper Api",
        routes=app.routes,
    )

    openapi_schema["info"]["x-logo"] = {"url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"}

    app.openapi_schema = openapi_schema

    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    # $ uvicorn main:app --reload
    port = config("FASTAPI_LOCAL_PORT", cast=int)
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload="True")
