import torch
import torchvision

print(torch.__version__, torch.cuda.is_available())
# assert torch.__version__.startswith("1.9")   # please manually install torch 1.9 if Colab changes its default version
from detectron2.utils.logger import setup_logger

setup_logger()
torch.cuda.empty_cache()

import asyncio
import gc
import json
import os
import time
from pathlib import Path
from urllib.parse import urlparse

import aiofiles
import aiohttp
import cv2

# import some common libraries
import wget
from decouple import config

# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog
from detectron2.engine import DefaultPredictor
from fastapi import HTTPException
from models import fetch_image_from_url, insert_object, update_detectron_frame_flags

# from detectron2.utils.visualizer import Visualizer
from pdPredict import Visualizer

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

time_list = []


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


async def insert_detectron_object(frame_no, video_name, data, frame_id, video_id):

    if not data[0][3]:
        response = {
            "frame_no": frame_no,
            "frame_id": frame_id,
            "video_name": video_name,
            "video_id": video_id,
            "object_": "detectron",
            "attribute_": "confidence",
            "value_": "",
        }
    else:
        response = [
            {
                "frame_no": frame_no,
                "frame_id": frame_id,
                "video_name": video_name,
                "video_id": video_id,
                "object_": v1.split(" ")[0],
                "attribute_": "confidence",
                "value_": v1.split(" ")[-1],
            }
            for v1, v2 in zip(data[0][3], data[0][2])
        ]

    await insert_object(response)
    update_data = {"frame_no": frame_no, "video_name": video_name, "is_processed": 1}
    await update_detectron_frame_flags(update_data)


async def get_image(main_file_path):
    im = cv2.imread(main_file_path)
    return im


async def load_configuration():
    if not config("DOCKER_ENABLE", cast=bool):
        print("running from cuda")
        with torch.cuda.device(0):
            cfg = get_cfg()
            # add project-specific config (e.g., TensorMask) here if you're not running a model in detectron2's core library
            cfg.merge_from_file(
                model_zoo.get_config_file(
                    "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"
                )
            )
            cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
            # cfg.MODEL.DEVICE = "cuda"
            # Find a model from detectron2's model zoo. You can use the https://dl.fbaipublicfiles... url as well
            cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(
                "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"
            )
            cfg.MODEL.DEVICE = "cuda"
    else:
        cfg = get_cfg()
        # add project-specific config (e.g., TensorMask) here if you're not running a model in detectron2's core library
        cfg.merge_from_file(
            model_zoo.get_config_file(
                "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"
            )
        )
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
        # cfg.MODEL.DEVICE = "cuda"
        # Find a model from detectron2's model zoo. You can use the https://dl.fbaipublicfiles... url as well
        cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(
            "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"
        )
        cfg.MODEL.DEVICE = "cpu"
    print("model loaded done")
    return cfg


async def image_predictor(cfg, im):

    predictor = DefaultPredictor(cfg)
    # torch.cuda.synchronize()
    outputs = predictor(im)
    # torch.cuda.empty_cache()
    # print(outputs["instances"].pred_classes)
    # print(outputs["instances"].pred_boxes)

    v = Visualizer(
        im[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2
    )
    # out = v.draw_instance_predictions(outputs["instances"].to("cuda"))
    if not config("DOCKER_ENABLE", cast=bool):
        with torch.cuda.device(0):
            response = await v.get_only_lables(outputs["instances"].to("cuda"))
    else:
        response = await v.get_only_lables(outputs["instances"].to("cpu"))

    return response


async def pd_detectron2(main_file_path):
    frame_no = Path(main_file_path).parts[-1].split("_")[-1].split(".")[0]
    video_name = Path(main_file_path).parts[-2]
    confifuration_and_data = await asyncio.gather(
        asyncio.create_task(load_configuration()),
        asyncio.create_task(get_image(main_file_path)),
    )
    results = await asyncio.gather(
        asyncio.create_task(
            image_predictor(confifuration_and_data[0], confifuration_and_data[1])
        )
    )

    await asyncio.gather(
        asyncio.create_task(insert_detectron_object(frame_no, video_name, results))
    )
    gc.collect()
    torch.cuda.empty_cache()
    if len(results) > 0:
        return results[0]
    else:
        raise HTTPException(status_code=404, detail="text on an image not found")


@timeit
async def pd_detectron2_cloud(main_file_url, frame_id, video_id):
    frame_no = urlparse(main_file_url).path.split("_")[-1].split(".")[0]
    video_name = urlparse(main_file_url).path.split("/")[-2]
    confifuration_and_data = await asyncio.gather(
        asyncio.create_task(load_configuration()),
        asyncio.create_task(fetch_image_from_url(video_name, frame_no)),
    )
    print(confifuration_and_data)
    results = await asyncio.gather(
        asyncio.create_task(
            image_predictor(confifuration_and_data[0], confifuration_and_data[1])
        )
    )
    await asyncio.gather(
        asyncio.create_task(
            insert_detectron_object(frame_no, video_name, results, frame_id, video_id)
        )
    )
    if len(results) > 0:
        return results[0]
    else:
        raise HTTPException(status_code=404, detail="text on an image not found")


if __name__ == "__main__":
    main_file_path = "000000439715.jpg"
    if not os.path.exists(main_file_path):
        wget.download("http://images.cocodataset.org/val2017/000000439715.jpg")

    # Using cv2.imshow() method
    # Displaying the image
    im = cv2.imread(main_file_path)
    cv2.imshow("window_name", im)

    # waits for user to press any key
    # (this is necessary to avoid Python kernel form crashing)
    cv2.waitKey(222)

    # closing all open windows
    cv2.destroyAllWindows()
    pd_detectron2(im)
