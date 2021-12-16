import asyncio
import json
import time
from urllib.parse import urlparse

import aiofiles
import aiohttp
from decouple import config

from models import (fetch_image_from_url_rb, insert_object,
                    update_picpurify_frame_flags)


def timeit(func):
    async def process(func, *args, **params):
        if asyncio.iscoroutinefunction(func):
            print('this function is a coroutine: {}'.format(func.__name__))
            return await func(*args, **params)
        else:
            print('this is not a coroutine')
            return func(*args, **params)

    async def helper(*args, **params):
        print('{}.time'.format(func.__name__))
        start = time.time()
        result = await process(func, *args, **params)

        # Test normal function route...
        # result = await process(lambda *a, **p: print(*a, **p), *args, **params)
        final_time = time.time() - start
        async with aiofiles.open('time_data.txt', mode='a') as f:
            await f.write(f'\n{final_time},')
        print('\n\n\nTotal execution time for this function = {} >>>'.format(func.__name__),final_time, '\n\n\n')
        return result, final_time

    return helper

async def insert_picpurify_object(frame_no, video_name, data, frame_id, video_id):

    # NEeed to pix this
    response  = []
    update_data = {'frame_no':frame_no, 'video_name': video_name, 'is_pic_purified':1}
    if data['reject_criteria']:
        for mod in data['reject_criteria']:
            response.append({'frame_no':frame_no,
                'frame_id':frame_id,
                'video_id':video_id,
                'video_name':video_name,
                'object_':mod,
                'attribute_':'confidence',
                'value_': str(data[mod]['confidence_score']),
                })

        await insert_object(response)
        await update_picpurify_frame_flags(update_data)
    else:
        await update_picpurify_frame_flags(update_data)

async def perform_picpurify(main_file_url, frame_id, video_id, moderation):

    # API initialization params
    PIC_PURIFY_API=config('PIC_PURIFY_API', cast=str)
    PICPURIFY_ENDPOINT = config('PICPURIFY_ENDPOINT', cast=str)

    frame_no = urlparse(main_file_url).path.split('_')[-1].split('.')[0]
    video_name = urlparse(main_file_url).path.split('/')[-2]

    file_image = await asyncio.gather(
        asyncio.create_task(fetch_image_from_url_rb(video_name, frame_no))
        )

    async def make_api_asyc_call():
        form_data = aiohttp.FormData()
        form_data.add_field("API_KEY", PIC_PURIFY_API)
        form_data.add_field("task", moderation)
        form_data.add_field("file_image", file_image[0])

        async with aiohttp.ClientSession(json_serialize=json.dumps) as session:
                result_data = await session.post(PICPURIFY_ENDPOINT, data=form_data)
                print(await result_data.json(content_type=None))
                content = await result_data.json(content_type=None)
        await session.close()
        return content

    content = await make_api_asyc_call()

    await asyncio.gather(
        asyncio.create_task(
            insert_picpurify_object(frame_no, video_name, content, frame_id, video_id)
        )
    )

