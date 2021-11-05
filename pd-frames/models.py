from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text

from database import Base


from sqlalchemy.orm import Session
from database import SessionLocal, engine


from sqlalchemy.sql import text

def insert_frames(data=None):
    with engine.connect() as con:

        if data is None:
            print('data is missing to inesrt')
            return
        # data = ( { "frame_no": "The Hobbit", "video_frame": "Tolkien", 'frame_path': '/frame_rr' },
        #         { "frame_no": "The Hobbit2", "video_frame": "Tolkien", 'frame_path': '/frame_rb' }
        # )

        statement = text("""INSERT INTO table_2 (frame_no, video_frame, frame_path)\
            VALUES (:frame_no, :video_frame, :frame_path)""")
        # text("""INSERT INTO book(id, title, primary_author) VALUES(:id, :title, :primary_author)""")

        for line in data:
            con.execute(statement, **line)