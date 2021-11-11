import torch
import torchvision

print(torch.__version__, torch.cuda.is_available())
# assert torch.__version__.startswith("1.9")   # please manually install torch 1.9 if Colab changes its default version
from detectron2.utils.logger import setup_logger

setup_logger()
torch.cuda.empty_cache()

import asyncio
import json
import os
from pathlib import Path

import cv2
# import some common libraries
import numpy as np
import wget
from decouple import config
# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog
from detectron2.engine import DefaultPredictor
from fastapi import HTTPException
from models import insert_object, update_frame_flags
# from detectron2.utils.visualizer import Visualizer
from pdPredict import Visualizer

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

async def insert_detectron_object(frame_no, video_name, data):
    final_object  = {
        'data': [{"object": v1.split(" ")[0],"confidence": v1.split(" ")[1], 'class_lables': v2 }  for v1, v2 in  zip(data[0][3], data[0][2])],
        'class_lable_list' : data[0][2],
        # 'bbox_tensor' : data[0][0],
    }
    response = {'frame_no': frame_no, 'video_name': video_name, 'detectron_object': json.dumps(final_object)}
    await insert_object(response)
    update_data = {'frame_no':frame_no, 'video_name': video_name, 'is_processed':1}
    await update_frame_flags(update_data)
    # return response

async def get_image(main_file_path):
    im = cv2.imread(main_file_path)
    return im

async def url_to_image(response):
	# download the image, convert it to a NumPy array, and then read
	# it into OpenCV format
	image = np.asarray(bytearray(response.content), dtype="uint8")
	image = cv2.imdecode(image, cv2.IMREAD_COLOR)
	# return the image
	return image

async def load_configuration():
    cfg = get_cfg()
    # add project-specific config (e.g., TensorMask) here if you're not running a model in detectron2's core library
    cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
    # Find a model from detectron2's model zoo. You can use the https://dl.fbaipublicfiles... url as well
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
    if not config('DOCKER_ENABLE'):
        cfg.MODEL.DEVICE = "cuda"
    else:
        cfg.MODEL.DEVICE = "cpu"
    print('model loaded done')
    return cfg

async def image_predictor(cfg, im):
    predictor = DefaultPredictor(cfg)
    # torch.cuda.synchronize()
    outputs = predictor(im)
    # torch.cuda.empty_cache()

    v = Visualizer(im[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2)
    # out = v.draw_instance_predictions(outputs["instances"].to("cuda"))
    if not config('DOCKER_ENABLE'):
        response = await v.get_only_lables(outputs["instances"].to("cuda"))
    else:
        response = await v.get_only_lables(outputs["instances"].to("cpu"))

    return response

async def pd_detectron2(main_file_path):
    frame_no = Path(main_file_path).parts[-1].split('_')[-1].split('.')[0]
    video_name = Path(main_file_path).parts[-2]
    confifuration_and_data = await asyncio.gather(
        asyncio.create_task(load_configuration()),
        asyncio.create_task(get_image(main_file_path))
        )
    results = await asyncio.gather(asyncio.create_task(
        image_predictor(confifuration_and_data[0], confifuration_and_data[1])
        ))

    await asyncio.gather(
        asyncio.create_task(
            insert_detectron_object(frame_no, video_name, results)
        )
    )
    if len(results) > 0:
        return results[0]
    else:
        raise HTTPException(status_code=404, detail="text on an image not found")



if __name__ == "__main__":
    main_file_path = '000000439715.jpg'
    if not os.path.exists(main_file_path):
        wget.download("http://images.cocodataset.org/val2017/000000439715.jpg")

    # Using cv2.imshow() method
    # Displaying the image
    im = cv2.imread(main_file_path)
    cv2.imshow('window_name', im)

    #waits for user to press any key
    #(this is necessary to avoid Python kernel form crashing)
    cv2.waitKey(222)

    #closing all open windows
    cv2.destroyAllWindows()
    pd_detectron2(im)

