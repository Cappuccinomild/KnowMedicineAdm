import os

BASE_DIR = os.path.dirname(__file__)

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://test:1234@192.168.17.1/knowmedicine'
SQLALCHEMY_TRACK_MODIFICATIONS = False