from dotenv import load_dotenv
import os

load_dotenv()
polygon_token = os.environ.get('POLYGON_TOKEN')

def load_token():
    return polygon_token