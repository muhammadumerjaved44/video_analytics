import asyncio
import datetime
import os
from io import BytesIO

import cv2
from database import SessionLocal, engine
from decouple import config
from minio import Minio
from minio.error import ServerError
from PIL import Image
from sqlalchemy.sql import text

# minio keys setup
# host=config('MINIO_HOST', cast=str)
host = '172.25.0.3:9000'
access_key=config('MINIO_ACCESS_KEY', cast=str)
secret_key=config('MINIO_SECRET_KEY', cast=str)
bucket_name=config('MINIO_BUCKET_NAME', cast=str)

async def upload_frames(video_name, frame, frame_no):
    minio_client = Minio(host, access_key=access_key, secret_key=secret_key, secure=False)
    found = minio_client.bucket_exists(bucket_name)
    if not found:
        minio_client.make_bucket(bucket_name)
    else:
        print("Bucket 'frames' already exists")

    # im = cv2.imread('image_0.jpg')
    # # frame type convertion form cv2 to pil
    # frame = im
    # im_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image=Image.fromarray(frame.asnumpy())
    frame_stream = BytesIO()
    pil_image.save(frame_stream, format='JPEG')
    frame_stream.seek(0)
    frame_stream_size = frame_stream.getbuffer().nbytes

    try:
        frame_name_path = os.path.join(video_name, f"image_{frame_no}.jpg")
        minio_client.put_object(bucket_name, frame_name_path, frame_stream, frame_stream_size)
        image_url = minio_client.presigned_get_object(bucket_name, frame_name_path, expires=datetime.timedelta(hours=2))
        print(image_url)
        return image_url
    except:
        print('file not uploaded')


ses = SessionLocal()
async def insert_frames(data=None):
    # data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'file_path':'umer'}
    sess =  SessionLocal()
    with sess.connection() as con:

        if data is None:
            print('data is missing to inesrt')
            return

        statement = text("""INSERT INTO table_2 (frame_no, video_name, file_path, is_processed)\
            VALUES (:frame_no, :video_name, :file_path, :is_processed)""")

        try:
            con.execute(statement, data)
            print('please wait inserting frames')

            return True
        except:
            print('db connection not build / insertion failed')
            return False