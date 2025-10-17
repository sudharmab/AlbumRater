import certifi
import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
MONGODB_HOST = os.environ.get("MONGODB_HOST")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
print(CLIENT_SECRET, CLIENT_ID)

# testing to make sure this edit is made in nico branch
