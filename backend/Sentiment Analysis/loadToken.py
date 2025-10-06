from dotenv import load_dotenv
import os

load_dotenv()
POLYGON_TOKEN = os.environ.get('POLYGON_TOKEN')

def POLYGON_TOKEN():
    return POLYGON_TOKEN