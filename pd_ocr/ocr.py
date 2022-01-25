import asyncio
import gc
import glob
import os
import random
import re
import string
import time
from urllib.parse import urlparse

import aiofiles
import pandas as pd
import requests
import torch
from decouple import config
from easyocr import Reader
from nltk import word_tokenize
from PIL import Image
from textblob import TextBlob

from models import fetch_image_from_url, insert_object, update_frame_flags
from spell_correction import correction

base_path = os.path.dirname(os.path.abspath(__file__))

# gc.collect()
# torch.cuda.empty_cache()


time_list = []
# def timeit(func):
#     async def process(func, *args, **params):
#         if asyncio.iscoroutinefunction(func):
#             print("this function is a coroutine: {}".format(func.__name__))
#             return await func(*args, **params)
#         else:
#             print("this is not a coroutine")
#             return func(*args, **params)

#     async def helper(*args, **params):
#         print("{}.time".format(func.__name__))
#         start = time.time()
#         result = await process(func, *args, **params)

#         # Test normal function route...
#         # result = await process(lambda *a, **p: print(*a, **p), *args, **params)
#         final_time = time.time() - start
#         async with aiofiles.open("time_data.txt", mode="a") as f:
#             await f.write(f"\n{final_time},")
#         print(
#             "\n\n\nTotal execution time for this function = {} >>>".format(func.__name__),
#             final_time,
#             "\n\n\n",
#         )
#         return result, final_time

#     return helper


async def insert_text_object(
    frame_no,
    video_name,
    video_id,
    frame_id,
    simple_ouput_text,
    simple_ouput_text_oprated,
):

    response = {
        "frame_id": frame_id,
        "frame_no": frame_no,
        "video_name": video_name,
        "video_id": video_id,
        "object_": "ocr",
        "attribute_": "text",
        "value_": simple_ouput_text[0],
    }
    print("my responce ", response)

    await insert_object(response)
    update_data = {
        "frame_no": frame_no,
        "video_name": video_name,
        "is_ocr_processed": 1,
    }
    await update_frame_flags(update_data)


def random_string(N=6) -> str:
    """genrate random name for file saving

    Args:
        N (int, optional): random string length. Defaults to 6.

    Returns:
        str: resturn 6 letters random string
    """

    return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))


async def deepstack_image_discription(image_path: str) -> str:
    """scene recogination using deep stack library

    Args:
        image_path (str): gets the local file path as input

    Returns:
        [type]: [description]
    """

    image_data = open(image_path, "rb").read()
    response = requests.post("http://localhost:5123/v1/vision/scene", files={"image": image_data}).json()
    # print("Label:",response["label"])
    # print(response)

    return response["label"]


async def basic_post_processing(results: list) -> str:
    """pass the list of words for basic text preprocessing

    Args:
        results (list): list of words

    Returns:
        str: correted string
    """

    rep = {
        "\n": " ",
        "\\": " ",
        '"': '"',
        "-": " ",
        '"': ' " ',
        '"': ' " ',
        '"': ' " ',
        ",": " , ",
        ".": " . ",
        "!": " ! ",
        "?": " ? ",
        "n't": " not",
        "'ll": " will",
        "*": " * ",
        "(": " ( ",
        ")": " ) ",
        "s'": "s '",
        "&": " and",
    }
    rep = dict((re.escape(k), v) for k, v in rep.items())
    pattern = re.compile("|".join(rep.keys()))
    basic_correction = pattern.sub(lambda m: rep[re.escape(m.group(0))], results)

    return basic_correction


async def bolb_based_post_processing(results: list) -> str:
    """blob based text preprocessing

    Args:
        results (list): list of words

    Returns:
        str: bolb based correted string
    """

    results_data = await basic_post_processing(results)

    def find_blob(results_data):
        textBlb = TextBlob(results_data)  # Making our first textblob
        textCorrected = str(textBlb.correct())  # Correcting the text
        textCorrected = textCorrected.strip()  # clean up spaces
        blob_based_correction = re.sub("\s{2,}", " ", textCorrected)  # clean up spaces

        return blob_based_correction

    blob_based_correction = find_blob(results_data)
    return blob_based_correction


async def word_base_post_processing(results: list) -> str:
    """word based text preprocessing

    Args:
        results (list): list of words

    Returns:
        str: word based corrected string
    """

    results_data = await basic_post_processing(results)
    word_list = word_tokenize(results_data)
    correct_phrase_list = [correction(x) for x in word_list]
    word_based_correction = " ".join(correct_phrase_list).replace("/", "").replace("\\", "").lower()

    return word_based_correction


async def easyocr_read(file, reader):
    """
    easy ocr text recogination

    Args:
        file (str): required the open image in byte/file path
        reader (object): required the easy ocr model

    Returns:
        str: extracted text from the image
    """

    print("enter into reading mode")
    reader = Reader(
        ["en"],
        gpu=config("DOCKER_GPU_ENABLE", cast=bool),
        model_storage_directory=os.path.join(base_path, "easyocr_model"),
        download_enabled=False,
    )
    print(reader, file)
    results = reader.readtext(file)
    print("printing resutls", results)
    if not results:
        print("text not found", results)
        return results
    else:
        results = sorted(results, key=lambda x: x[0][0])
        print("umer is good", results, "\n")
        text_results = [x[-2] for x in results]  # get text
        easy_output = " ".join(text_results).replace("/", "").replace("\\", "").lower()  # join together
        easy_output = easy_output.strip()  # clean up spaces
        simple_ouput_text = re.sub("\s{2,}", " ", easy_output)  # clean up spaces

        return simple_ouput_text


# @timeit
async def main_ocr(main_file_url, frame_id, video_id, reader):
    frame_no = urlparse(main_file_url).path.split("_")[-1].split(".")[0]
    video_name = urlparse(main_file_url).path.split("/")[-2]
    image = await asyncio.gather(asyncio.create_task(fetch_image_from_url(video_name, frame_no)))
    print(image)
    simple_ouput_text = await asyncio.gather(asyncio.create_task(easyocr_read(image[0], reader)))
    print("simple output text ", simple_ouput_text)
    if not simple_ouput_text[0]:
        simple_ouput_text = [""]
        simple_ouput_text_oprated = ["", "", ""]
    else:
        simple_ouput_text_oprated = await asyncio.gather(
            asyncio.create_task(basic_post_processing(simple_ouput_text[0])),
            asyncio.create_task(bolb_based_post_processing(simple_ouput_text[0])),
            asyncio.create_task(word_base_post_processing(simple_ouput_text[0])),
        )
    print(simple_ouput_text_oprated)

    await asyncio.gather(
        asyncio.create_task(
            insert_text_object(
                frame_no,
                video_name,
                video_id,
                frame_id,
                simple_ouput_text,
                simple_ouput_text_oprated,
            )
        )
    )
    # gc.collect()
    # torch.cuda.empty_cache()


if __name__ == "__main__":
    image_dir_path = "img/*.jpg"

    image_paths = glob.glob(image_dir_path)

    image_path_list = []
    simple_ouput_text_list = []
    basic_correction_list = []
    blob_based_correction_list = []
    word_based_correction_list = []
    deepstack_text_list = []

    for image_path in image_paths:

        simple_ouput_text = easyocr_read(image_path, reader)

        # post correction
        basic_correction = basic_post_processing(simple_ouput_text)
        blob_based_correction = bolb_based_post_processing(simple_ouput_text)
        word_based_correction = word_base_post_processing(simple_ouput_text)

        # Deep stack scene discription
        deepstack_text = deepstack_image_discription(image_path)

        print(
            simple_ouput_text,
            basic_correction,
            blob_based_correction,
            word_based_correction,
            deepstack_text,
        )

        image_path_list.append(image_path)
        simple_ouput_text_list.append(simple_ouput_text)
        basic_correction_list.append(basic_correction)
        blob_based_correction_list.append(blob_based_correction)
        word_based_correction_list.append(word_based_correction)
        deepstack_text_list.append(deepstack_text)

        img = Image.open(image_path)
        try:
            img.save("image_text/" + simple_ouput_text + " | " + word_based_correction + ".jpg")
        except:
            print("file not saved")

    details = {
        "image_path": image_path_list,
        "simple_ouput_text": simple_ouput_text_list,
        "basic_correction": basic_correction_list,
        "blob_based_correction": blob_based_correction_list,
        "word_based_correction": word_based_correction_list,
        "deepstack_text": deepstack_text_list,
    }
    df = pd.DataFrame(details)
    df.to_csv("text_results.csv")
