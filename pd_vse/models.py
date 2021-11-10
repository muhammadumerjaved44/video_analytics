from database import engine, SessionLocal
from sqlalchemy.sql import text

ses = SessionLocal()
async def get_frames():
    # data = { "frame_no": "The Hobbit", "video_name": "Tolkien", 'file_path':'umer'}
    sess =  SessionLocal()
    with sess.connection() as con:
        statement = text("""SELECT * from table_2""")

        try:
            results = con.execute(statement)
            data = results.fetchall()
            print('please wait inserting frames')
        except:
            print('db connection not build / insertion failed')

    return data