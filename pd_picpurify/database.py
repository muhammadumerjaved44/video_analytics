import sqlalchemy
from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# todo: async connection comes here
# not working with mmsql
# from sqlalchemy.ext.asyncio import create_async_engine
# from sqlalchemy.ext.asyncio import AsyncSession

db_host = config("MSSQL_LOCAL_HOST", cast=str)
db_port = config("MSSQL_LOCAL_PORT", default=1433, cast=int)
db_user = config("MSSQL_ROOT_USERNAME", default="root")
db_pass = config("MSSQL_ROOT_PASSWORD", default="root")
db_name = config("MSSQL_DB", default="point_duty")


engine = create_engine(
    # Equivalent URL:
    # mysql+pymysql://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
    sqlalchemy.engine.url.URL.create(
        drivername="mssql+pyodbc",
        username=db_user,  # e.g. "my-database-user"
        password=db_pass,  # e.g. "my-database-password"
        host=db_host,  # e.g. "127.0.0.1"
        port=db_port,  # e.g. 3306
        database=db_name,  # e.g. "my-database-name"
        query={
            "driver": "ODBC Driver 17 for SQL Server",  # make sure install mssql in local/docker
        },
    ),
    echo=True,
    pool_size=2,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=True, autoflush=False, bind=engine)

Base = declarative_base()
