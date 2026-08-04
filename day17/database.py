from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
DB_USER="root"
DB_PASSWORD="123456"
DB_HOST="localhost"
DB_PORT=3306
DB_NAME="ai_dataset_db"
DATABASE_URL=f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
engine=create_engine(DATABASE_URL,echo=True)
SessionLocal=sessionmaker(bind=engine)
Base=declarative_base()