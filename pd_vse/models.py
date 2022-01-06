from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from database import SessionLocal, engine

# ses = SessionLocal()


async def get_ocr_frames(db: Session):
    # data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'file_path':'umer'}
    with db.connection() as con:
        statement = text("""SELECT * from table_2 WHERE is_ocr_processed=0""")

        try:
            query_response = con.execute(statement)
            data = [{column: value for column, value in rowproxy.items()} for rowproxy in query_response]
            print("please wait inserting frames")
        except:
            print("db connection not build / insertion failed")

    return data


async def get_detectron_frames(db: Session):
    # data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'file_path':'umer'}
    with db.connection() as con:
        statement = text("""SELECT * from table_2 WHERE is_processed=0""")

        try:
            query_response = con.execute(statement)
            data = [{column: value for column, value in rowproxy.items()} for rowproxy in query_response]
            print("please wait inserting frames")
        except:
            print("db connection not build / insertion failed")

    return data


async def get_picpurify_frames(db: Session):
    # data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'file_path':'umer'}
    with db.connection() as con:
        statement = text("""SELECT * from table_2 WHERE is_pic_purified=0""")

        try:
            query_response = con.execute(statement)
            data = [{column: value for column, value in rowproxy.items()} for rowproxy in query_response]
            print("please wait inserting frames")
        except:
            print("db connection not build / insertion failed")

    return data


async def get_qr_frames(db):
    # data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'file_path':'umer'}
    with db.connection() as con:
        statement = text("""SELECT * from table_2 WHERE is_qr_processed=0""")

        try:
            query_response = con.execute(statement)
            data = [{column: value for column, value in rowproxy.items()} for rowproxy in query_response]
            print("please wait inserting frames")
        except:
            print("db connection not build / insertion failed")

    return data


async def get_predictions(db: Session):
    # data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'file_path':'umer'}
    with db.connection() as con:
        statement = text("""SELECT * from table_1""")

        try:
            results = con.execute(statement)
            data = results.fetchall()
            print("please wait fetching frames")
        except:
            print("db connection not build / insertion failed")

    return data


async def get_counts(db: Session):
    # data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'file_path':'umer'}
    with db.connection() as con:
        statement = text("""SELECT count(*) from table_1""")

        try:
            results = con.execute(statement)
            data = results.fetchall()
            print("please wait counting frames")
        except:
            print("db connection not build / insertion failed")

    return {"count": data[0][0]}


async def insert_object(db: Session, data=None):
    # data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'detectron_object':'umer'}
    if data is None:
        print("data is missing to inesrt")
        # return
    # data = {'frame_no':0, 'frame_id':44820, 'video_id':12, 'video_name':'Bad_fire.mp4', 'object_':'object_', 'attribute_':'attribute_', 'value_': 'value_'}

    statement = text(
        """INSERT INTO table_1 (frame_no, frame_id, video_id, video_name, object_, attribute_, value_) \
        VALUES (:frame_no, :frame_id, :video_id, :video_name, :object_, :attribute_, :value_)"""
    )

    # sess =  SessionLocal()
    with db.connection() as con:
        with con.begin():
            try:
                con.execute(statement, data)
                print("please wait inserting frames")

                # return True
            except:
                print("db connection not build / insertion failed")
                # return False


async def check_in_progress_videos():
    sess = SessionLocal()
    with sess.connection() as con:
        statement = text("""SELECT TOP(1) * FROM table_3 WHERE is_in_progress=1""")
        try:
            results = con.execute(statement)
            data = results.fetchall()
            if len(data) > 0:
                is_in_progress = True
            else:
                is_in_progress = False
            print("please getting unprocessed frames")
            # return True
        except:
            print("db connection not build / insertion failed")

    return is_in_progress
