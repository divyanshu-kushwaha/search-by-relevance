import csv
import os

import pymongo
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')

# Connect to MongoDB Atlas
client = pymongo.MongoClient(MONGO_URI)
db = client["SixtyFour"]
collection = db["items"]

csv_file = 'MetaDataSample.csv'

# Inserting each entry from the csv file into the Database
with open(csv_file, 'r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        collection.insert_one(row)
