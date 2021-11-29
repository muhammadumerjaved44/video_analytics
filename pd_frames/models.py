import asyncio
import datetime
import os
from io import BytesIO
from pathlib import Path

import cv2
from decouple import config
from minio import Minio
from minio.error import ServerError
from PIL import Image
from sqlalchemy.sql import text

from database import SessionLocal, engine

# minio keys setup
host=config('MINIO_HOST', cast=str)
access_key=config('MINIO_ACCESS_KEY', cast=str)
secret_key=config('MINIO_SECRET_KEY', cast=str)

async def upload_video(video_file):
    bucket_name = 'videos'
    minio_client = Minio(host, access_key=access_key, secret_key=secret_key, secure=False)
    found = minio_client.bucket_exists(bucket_name)
    if not found:
        minio_client.make_bucket(bucket_name)
    else:
        print("Bucket 'videos' already exists")

    try:
        result = minio_client.fput_object(bucket_name, Path(video_file).name, video_file)
        video_url = minio_client.presigned_get_object(bucket_name, Path(video_file).name, expires=datetime.timedelta(hours=48))
        return video_url, result.version_id
    except:
        print('file not uploaded')

async def insert_video(data=None):
    #data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'file_path':'umer', 'is_processed': 0}
    sess =  SessionLocal()
    with sess.connection() as con:

        if data is None:
            print('data is missing to inesrt')
            # return

        statement = text("""INSERT INTO table_3 (video_name, version_id, is_video_processed, is_in_progress, video_url)\
            VALUES (:video_name, :version_id, :is_video_processed, :is_in_progress, :video_url)""")

        try:
            con.execute(statement, data)
            print('please wait inserting frames')

            # return True
        except:
            print('db connection not build / insertion failed')

async def upload_frames(video_name, frame, frame_no):
    bucket_name = 'frames'
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
        image_url = minio_client.presigned_get_object(bucket_name, frame_name_path, expires=datetime.timedelta(hours=48))
        print(image_url)
        return image_url
    except:
        print('file not uploaded')


async def insert_frames(data=None):
    #data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'file_path':'umer', 'is_processed': 0}
    sess =  SessionLocal()
    with sess.connection() as con:

        if data is None:
            print('data is missing to inesrt')
            # return
        # id	video_id	frame_no	video_name	file_path	is_processed	is_ocr_processed
        statement = text("""INSERT INTO table_2 (video_id, frame_no, video_name, file_path, is_processed, is_ocr_processed)\
            VALUES (:video_id, :frame_no, :video_name, :file_path, :is_processed, :is_ocr_processed)""")

        try:
            con.execute(statement, data)
            print('please wait inserting frames')

            # return True
        except:
            print('db connection not build / insertion failed')
            # return False


async def get_videos():
    #data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'file_path':'umer', 'is_processed': 0}
    sess =  SessionLocal()
    with sess.connection() as con:
        statement = text("""SELECT TOP(1) * FROM table_3 WHERE is_video_processed=0""")

        try:
            query_response = con.execute(statement)
            # data = results.fetchall()
            data = [{column: value for column, value in rowproxy.items()} for rowproxy in query_response]
            print('please getting unprocessed frames')
            # return True
        except:
            print('db connection not build / insertion failed')
    
    sess =  SessionLocal()
    for record in data:
        print(record['id'])
        with sess.connection() as con:
            statement_update = text("""UPDATE table_3 SET is_in_progress=1 WHERE id=:id""")
            try:
                results = con.execute(statement_update, {"id":record['id']})
                print('please wait updating processed video frames')
                # return True
            except:
                print('db connection not build / insertion failed')
    return data

async def update_progress_video_flag(data):

    sess =  SessionLocal()
    with sess.connection() as con:

        if data is None:
            print('data is missing to inesrt')
            # return
        # id	video_id	frame_no	video_name	file_path	is_processed	is_ocr_processed
        statement = text("""UPDATE table_3 SET is_in_progress=:is_in_progress, is_video_processed=:is_video_processed  WHERE id=:id""")

        try:
            con.execute(statement, data)
            print('please wait inserting frames')

            # return True
        except:
            print('db connection not build / insertion failed')
            # return False
async def check_any_videos_left():
    sess =  SessionLocal()
    with sess.connection() as con:
        statement = text("""SELECT TOP(1) * FROM table_3 WHERE is_video_processed=0""")
        try:
            results = con.execute(statement)
            data = results.fetchall()
            if len(data)>0:
                is_any_video_left = True
            else:
                is_any_video_left = False
            print('please getting unprocessed frames')
            # return True
        except:
            print('db connection not build / insertion failed')

    return is_any_video_left

async def check_in_progress_videos():
    sess =  SessionLocal()
    with sess.connection() as con:
        statement = text("""SELECT TOP(1) * FROM table_3 WHERE is_in_progress=1""")
        try:
            results = con.execute(statement)
            data = results.fetchall()
            if len(data)>0:
                is_in_progress = True
            else:
                is_in_progress = False
            print('please getting unprocessed frames')
            # return True
        except:
            print('db connection not build / insertion failed')

    return is_in_progress


async def get_videos_as_object():
    bucket_name = 'videos'
    minio_client = Minio(host, access_key=access_key, secret_key=secret_key, secure=False)
    found = minio_client.bucket_exists(bucket_name)
    if not found:
        minio_client.make_bucket(bucket_name)
    else:
        print("Bucket 'videos' already exists")

    try:
        response = minio_client.presigned_get_object(bucket_name, 'file_example_MP4_1280_10MG.mp4',
                                           version_id='dda4f765-7227-4997-b1a0-805996e6300c',  expires=datetime.timedelta(hours=48))
        with open('my-testfile.mp4', 'wb') as file_data:
            for d in response.stream(32*1024):
                file_data.write(d)
    finally:
        response.close()
        response.release_conn()

async def get_unprocessed_videos_urls(data):
    # data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'file_path':'umer'}
    # data = {'id': 2}
    sess =  SessionLocal()
    with sess.connection() as con:
        statement = text("""SELECT * FROM table_3 WHERE id=:id""")

        try:
            query_response = con.execute(statement, data)
            # results = query_response.fetchall()res
            results = [{column: value for column, value in rowproxy.items()} for rowproxy in query_response]
            print('please wait inserting frames')
        except:
            print('db connection not build / insertion failed')


    bucket_name = 'videos'
    minio_client = Minio(host, access_key=access_key, secret_key=secret_key, secure=False)
    found = minio_client.bucket_exists(bucket_name)
    if not found:
        minio_client.make_bucket(bucket_name)
    else:
        print("Bucket 'videos' already exists")

    try:
        video_url = minio_client.presigned_get_object(bucket_name, results[0]['video_name'], version_id=results[0]['version_id'], expires=datetime.timedelta(hours=48))
        return video_url
    except:
        print('file not uploaded')
