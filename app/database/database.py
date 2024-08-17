from app.resources.config import DB_URL
from pymongo import MongoClient

client: MongoClient = MongoClient(DB_URL)
db = client.test_database

# create admin
# site data
# project images

def create_admin(email: str, password: str):
	pass


	# db.create_collection(names)