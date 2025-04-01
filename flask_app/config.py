import certifi
import os

SECRET_KEY = os.environ.get("SECRET_KEY")
MONGODB_HOST = os.environ.get("MONGODB_HOST") + certifi.where()


# testing to make sure this edit is made in nico branch
