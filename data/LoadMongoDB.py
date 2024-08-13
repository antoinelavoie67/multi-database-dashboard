import json
from pymongo import MongoClient

# Making Connection
myclient = MongoClient("mongodb://localhost:27017/")

# database
db = myclient["academicworld"]

# Loading or Opening the json file
with open('faculty.json') as file:
	file_data = json.load(file)

# Created or Switched to collection
Collection = db["faculty"]

# Inserting the loaded data in the Collection
# if JSON contains data more than one entry
# insert_many is used else inser_one is used
if isinstance(file_data, list):
	Collection.insert_many(file_data)
else:
	Collection.insert_one(file_data)


with open('publications.json') as file:
	file_data = json.load(file)

Collection = db["publications"]

if isinstance(file_data, list):
	Collection.insert_many(file_data)
else:
	Collection.insert_one(file_data)