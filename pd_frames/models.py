from database import engine, SessionLocal
from sqlalchemy.sql import text

ses = SessionLocal()
async def insert_frames(data=None):
    # data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'file_path':'umer'}
    sess =  SessionLocal()
    with sess.connection() as con:

        if data is None:
            print('data is missing to inesrt')
            return

        statement = text("""INSERT INTO table_2 (frame_no, video_name, file_path)\
            VALUES (:frame_no, :video_name, :file_path)""")

        try:
            con.execute(statement, data)
            print('please wait inserting frames')

            return True
        except:
            print('db connection not build / insertion failed')
            return False