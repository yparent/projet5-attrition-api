import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


from dotenv import load_dotenv
load_dotenv()


from app.database import engine
from app.db_models import Base


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    print('Tables creees avec succes sur Neon !')
