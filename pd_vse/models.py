from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from database import SessionLocal, engine


# ses = SessionLocal()

async def get_OCR_frames(db: Session):
    # data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'file_path':'umer'}
    with db.connection() as con:
        statement = text("""SELECT * from table_2 WHERE is_ocr_processed=0""")

        try:
            query_response = con.execute(statement)
            data = [{column: value for column, value in rowproxy.items()} for rowproxy in query_response]
            print('please wait inserting frames')
        except:
            print('db connection not build / insertion failed')

    return data

async def get_detectron_frames(db: Session):
    # data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'file_path':'umer'}
    with db.connection() as con:
        statement = text("""SELECT * from table_2 WHERE is_processed=0""")

        try:
            query_response = con.execute(statement)
            data = [{column: value for column, value in rowproxy.items()} for rowproxy in query_response]
            print('please wait inserting frames')
        except:
            print('db connection not build / insertion failed')

    return data

async def get_picpurify_frames(db: Session):
    # data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'file_path':'umer'}
    with db.connection() as con:
        statement = text("""SELECT * from table_2 WHERE is_pic_purified=0""")

        try:
            query_response = con.execute(statement)
            data = [{column: value for column, value in rowproxy.items()} for rowproxy in query_response]
            print('please wait inserting frames')
        except:
            print('db connection not build / insertion failed')

    return data

async def get_qr_frames(db: Session):
    # data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'file_path':'umer'}
    with db.connection() as con:
        statement = text("""SELECT * from table_2 WHERE is_qr_processed=0""")

        try:
            query_response = con.execute(statement)
            data = [{column: value for column, value in rowproxy.items()} for rowproxy in query_response]
            print('please wait inserting frames')
        except:
            print('db connection not build / insertion failed')

    return data



async def get_predictions(db: Session):
    # data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'file_path':'umer'}
    with db.connection() as con:
        statement = text("""SELECT * from table_1""")

        try:
            results = con.execute(statement)
            data = results.fetchall()
            print('please wait fetching frames')
        except:
            print('db connection not build / insertion failed')

    return data

async def get_counts(db: Session):
    # data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'file_path':'umer'}
    with db.connection() as con:
        statement = text("""SELECT count(*) from table_1""")

        try:
            results = con.execute(statement)
            data = results.fetchall()
            print('please wait counting frames')
        except:
            print('db connection not build / insertion failed')

    return {'count': data[0][0]}


async def insert_object(db: Session, data=None):
    #data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'detectron_object':'umer'}
    if data is None:
        print('data is missing to inesrt')
        # return
    # data = {'frame_no':0, 'frame_id':44820, 'video_id':12, 'video_name':'Bad_fire.mp4', 'object_':'object_', 'attribute_':'attribute_', 'value_': 'value_'}

    statement = text("""INSERT INTO table_1 (frame_no, frame_id, video_id, video_name, object_, attribute_, value_) \
        VALUES (:frame_no, :frame_id, :video_id, :video_name, :object_, :attribute_, :value_)""")

    # sess =  SessionLocal()
    with db.connection() as con:
        with con.begin():
            try:
                con.execute(statement, data)
                print('please wait inserting frames')

                # return True
            except:
                print('db connection not build / insertion failed')
                # return False


async def get_unprocessed_frame_url(data):
    # data = {'id':152, 'video_id':1}
    sess =  SessionLocal()
    with sess.connection() as con:
        statement = text("""SELECT * FROM table_2 WHERE id=:id and  video_id=:video_id and is_processed=0""")

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