from sqlalchemy.orm import Session
from sqlalchemy.sql import text


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

async def get_frames(db: Session):
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