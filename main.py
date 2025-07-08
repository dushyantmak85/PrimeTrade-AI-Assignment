from dotenv import load_dotenv
from binance.client import Client
import time
import requests
import os

# Load keys
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")



# Setup client
client = Client(API_KEY, API_SECRET)


print(client.get_account())

