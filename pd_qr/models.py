import datetime
import os

from decouple import config
from minio import Minio
from sqlalchemy.sql import text
import cv2
import numpy as np

from database import SessionLocal

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
    statement = text("""INSERT INTO table_1 (frame_no, frame_id, video_id, video_name, object_, attribute_, value_) \
        VALUES (:frame_no, :frame_id, :video_id, :video_name, :object_, :attribute_, :value_)""")

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

async def update_qr_frame_flags(data):
    # data = {'frame_no': '1', 'video_name': 'videoplayback.mp4', 'is_processed': 1}
    statement = text(f"""UPDATE table_2 SET is_qr_processed=:is_qr_processed WHERE frame_no=:frame_no and video_name=:video_name""")
    sess =  SessionLocal()
    with sess.connection() as connection:
        with connection.begin():
            try:
                connection.execute(statement, data)
                print('please wait table 2 updateing frames')

            except:
                print('db connection not build / insertion failed')


async def get_unprocessed_qr_frame_url(data):
    # data = {'id':152, 'video_id':1}
    sess =  SessionLocal()
    with sess.connection() as con:
        statement = text("""SELECT * FROM table_2 WHERE id=:id and video_id=:video_id and is_qr_processed=0""")

        try:
            query_response = con.execute(statement, data)
            # results = query_response.fetchall()
            results = [{column: value for column, value in rowproxy.items()} for rowproxy in query_response]
            print('please wait inserting frames')
        except:
            print('db connection not build / insertion failed')


    bucket_name = 'frames'
    minio_client = Minio(host, access_key=access_key, secret_key=secret_key, secure=False)
    found = minio_client.bucket_exists(bucket_name)
    if not found:
        minio_client.make_bucket(bucket_name)
    else:
        print("Bucket 'videos' already exists")

    try:
        folder_name = results[0]['video_name']
        frame_no = results[0]['frame_no']
        image_cloud_path = os.path.join(folder_name, f"image_{frame_no}.jpg")
        frame_url = minio_client.presigned_get_object(bucket_name, image_cloud_path, expires=datetime.timedelta(hours=48))
        return frame_url
    except:
        print('file not uploaded')