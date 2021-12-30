import asyncio
import codecs
import time
from urllib.parse import urlparse

import aiofiles
import cv2
from models import fetch_image_from_url, insert_object, update_qr_frame_flags
from pyzbar import pyzbar


def timeit(func):
    async def process(func, *args, **params):
        if asyncio.iscoroutinefunction(func):
            print("this function is a coroutine: {}".format(func.__name__))
            return await func(*args, **params)
        else:
            print("this is not a coroutine")
            return func(*args, **params)

    async def helper(*args, **params):
        print("{}.time".format(func.__name__))
        start = time.time()
        result = await process(func, *args, **params)

        # Test normal function route...
        # result = await process(lambda *a, **p: print(*a, **p), *args, **params)
        final_time = time.time() - start
        async with aiofiles.open("time_data.txt", mode="a") as f:
            await f.write(f"\n{final_time},")
        print(
            "\n\n\nTotal execution time for this function = {} >>>".format(
                func.__name__
            ),
            final_time,
            "\n\n\n",
        )
        return result, final_time

    return helper


async def insert_qr_object(frame_no, video_name, data, frame_id, video_id):

    response = {
        "frame_no": frame_no,
        "frame_id": frame_id,
        "video_id": video_id,
        "video_name": video_name,
        "object_": "qr_code",
        "attribute_": "text",
        "value_": data,
    }

    await insert_object(response)

    update_data = {"frame_no": frame_no, "video_name": video_name, "is_qr_processed": 1}
    await update_qr_frame_flags(update_data)


@timeit
async def qr_to_text(main_file_url, frame_id, video_id):
    frame_no = urlparse(main_file_url).path.split("_")[-1].split(".")[0]
    video_name = urlparse(main_file_url).path.split("/")[-2]
    image = await asyncio.gather(
        asyncio.create_task(fetch_image_from_url(video_name, frame_no))
    )
    # image = cv2.imread(main_file_url)
    # print(image)
    try:
        barcodes = pyzbar.decode(image[0])
        print("\n\n\n\n", barcodes)
    except:
        print("image dose not have qr code")
        barcodes = False
    if barcodes:
        final_string = (
            codecs.decode(barcodes[0].data.decode(), "unicode_escape")
            .replace("\r", " ")
            .strip()
        )
    else:
        final_string = ""

    await insert_qr_object(frame_no, video_name, final_string, frame_id, video_id)
    return final_string
