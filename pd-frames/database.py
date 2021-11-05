from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config


db_host = config('MYSQL_LOCAL_HOST', default='localhost')
db_port = config('MYSQL_LOCAL_PORT', default=3305, cast=int)
db_user = config('MYSQL_LOCAL_USER', default='root')
db_pass = config('MYSQL_LOCAL_PASS', default='root')
db_name   = config('MYSQL_LOCAL_DB', default='point_duty')


engine = create_engine(
    # Equivalent URL:
    # mysql+pymysql://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
    sqlalchemy.engine.url.URL.create(
        drivername="mysql+pymysql",
        username=db_user,  # e.g. "my-database-user"
        password=db_pass,  # e.g. "my-database-password"
        host=db_host,  # e.g. "127.0.0.1"
        port=db_port,  # e.g. 3306
        database=db_name,  # e.g. "my-database-name"
    ),
    echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()