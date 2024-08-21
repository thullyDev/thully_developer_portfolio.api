from typing import Any, Dict, Optional, List

from fastapi import responses
from app.resources.config import DB_URL
from pymongo import MongoClient

from app.resources.misc import datenow

client: MongoClient = MongoClient(DB_URL)
db = client.test_database
admin_collection = db.admins
sites_collection = db.sites 
projects_collection = db.projects


def update_site_data(data: Dict[str, Any]) -> bool:
	update_query = { "$set": { "data": data } }
	response = projects_collection.update_one({ "site": "thully_developer_portfolio" }, update_query)
	result = response.raw_result
	
	if result:
		return result["updatedExisting"] 

	return response.acknowledged

def set_site_data(data: Dict[str, Any]) -> bool:
	response = projects_collection.insert_one({ "site": "thully_developer_portfolio", "data": data })

	return response.acknowledged


def get_site_data() -> Optional[Dict[str, Any]]:
	return projects_collection.find_one({ "site": "thully_developer_portfolio" })


def create_admin(email: str, password: str) -> bool:
	response = admin_collection.insert_one({ "email": email, "password": password, "session_token": "", "created_at": datenow() })
	
	return response.acknowledged

def get_admin(email: str) -> Optional[Dict[str, Any]]:
	return admin_collection.find_one({ "email": email })

def get_project(repo_slug: str) -> Optional[Dict[str, Any]]:
	project = projects_collection.find_one({ "repo_slug": repo_slug })

	if not project:
		return 

	return project

def update_admin_token(email: str, session_token: str) -> bool:
	update_query = { "$set": { "session_token": session_token } }
	response = admin_collection.update_one({ "email": email }, update_query)
	
	return response.acknowledged

def upload_project(repo_slug: str, images: List[str]):
	response = projects_collection.insert_one({ "images": images, "repo_slug": repo_slug,  "created_at": datenow() })

	return response.acknowledged

def update_project_images(repo_slug: str, images: List[str]) -> bool:
	update_query = { "$set": { "images": images } }
	response = projects_collection.update_one({ "repo_slug": repo_slug }, update_query)
	
	return response.acknowledged

def delete_project(repo_slug: str) -> bool:
	response = projects_collection.delete_one({ "repo_slug": repo_slug })
	
	return response.acknowledged
