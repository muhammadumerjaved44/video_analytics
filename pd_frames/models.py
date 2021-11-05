from database import engine
from sqlalchemy.sql import text


def insert_frames(data=None):
    # data = [{ "frame_no": "The Hobbit", "video_frame": "Tolkien", 'frame_path': '/frame_rr' },
    #         { "frame_no": "The Hobbit2", "video_frame": "Tolkien", 'frame_path': '/frame_rb' }
    #         ]
    with engine.connect() as con:

        if data is None:
            print('data is missing to inesrt')
            return

        statement = text("""INSERT INTO table_2 (frame_no, video_name)\
            VALUES (:frame_no, :video_name)""")
        try:
            for line in data:

                con.execute(statement, **line)
                print('please wait inserting frames')

            return True
        except:
            print('db connection not build / insertion failed')
            return False