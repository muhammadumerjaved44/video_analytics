from database import SessionLocal
from sqlalchemy.sql import text

ses = SessionLocal()
async def insert_object(data=None):
    # data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'detectron_object':'umer'}
    if data is None:
        print('data is missing to inesrt')
        # return
    statement = text("""INSERT INTO table_1 (frame_no, video_name, detectron_object) VALUES (:frame_no, :video_name, :detectron_object)""")
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