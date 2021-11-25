import datetime
import os
from io import BytesIO

import cv2
import numpy as np
from database import SessionLocal
from decouple import config
from minio import Minio
from minio.error import ServerError
from sqlalchemy.sql import text

host=config('MINIO_HOST', cast=str)
access_key=config('MINIO_ACCESS_KEY', cast=str)
secret_key=config('MINIO_SECRET_KEY', cast=str)
bucket_name=config('MINIO_BUCKET_NAME', cast=str)

async def fetch_image_from_url(video_name, frame_no):
    minio_client = Minio(host, access_key=access_key, secret_key=secret_key, secure=False)
    found = minio_client.bucket_exists(bucket_name)
    if not found:
        minio_client.make_bucket(bucket_name)
    else:
        print("Bucket 'frames' already exists")

    try:
        frame_name_path = os.path.join(video_name, f"image_{frame_no}.jpg")
        response = minio_client.get_object(bucket_name, frame_name_path)
        # image = Image.open(BytesIO(response.data))
        image = np.asarray(bytearray(response.data), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return image
    except:
        print('image not found')

ses = SessionLocal()
async def insert_object(data=None):
    #data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'detectron_object':'umer'}
    if data is None:
        print('data is missing to inesrt')
        # return
    # id	frame_no	video_id	video_name	detectron_object	ocr_object
    statement = text("""INSERT INTO table_1 (frame_no, video_id, video_name, object_, value_, detectron_object) \
        VALUES (:frame_no, :video_id, :video_name, :object_, :value_, :detectron_object)""")

    sess =  SessionLocal()
    with sess.connection() as connection:
        with connection.begin():
            try:
                connection.execute(statement, data)
                print('please wait inserting frames')

                # return True
            except:
                print('db connection not build / insertion failed')
                # return False

async def update_frame_flags(data):
    # data = {'frame_no': '1', 'video_name': 'videoplayback.mp4', 'is_processed': 1}
    statement = text(f"""UPDATE table_2 SET is_processed=:is_processed WHERE frame_no=:frame_no and video_name=:video_name""")
    sess =  SessionLocal()
    with sess.connection() as connection:
        with connection.begin():
            try:
                connection.execute(statement, data)
                print('please wait table 2 updateing frames')

            except:
                print('db connection not build / insertion failed')