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