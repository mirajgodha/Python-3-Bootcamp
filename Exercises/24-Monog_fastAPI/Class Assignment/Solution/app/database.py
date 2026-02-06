from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client.tasks_db
tasks_col = db.tasks
