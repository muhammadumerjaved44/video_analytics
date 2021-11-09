from database import engine
from sqlalchemy.sql import text


async def insert_frames(data=None):
    # data = { "frame_no": "The Hobbit", "video_name": "Tolkien"}

    with engine.connect() as con:

        if data is None:
            print('data is missing to inesrt')
            return

        statement = text("""INSERT INTO table_2 (frame_no, video_name)\
            VALUES (:frame_no, :video_name)""")

        try:
            con.execute(statement, data)
            print('please wait inserting frames')

            return True
        except:
            print('db connection not build / insertion failed')
            return False