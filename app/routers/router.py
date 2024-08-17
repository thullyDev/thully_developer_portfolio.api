from typing import Any, List, Optional, Dict
from fastapi import APIRouter
from app.handlers import response_handler as response
from app.database import database
from app.resources.config import SITE_KEY
from app.resources.misc import generate_unique_token

router: APIRouter = APIRouter(prefix="/api")

@router.get("/login/")
def login(email: str, password: str):
     if len(password) < 10:
          return response.bad_request_response(message="password should have atleast 10 characters")

     admin = database.get_admin(email)

     if not admin:
          return response.forbidden_response(message="invalid admin")

     admin_password = admin["password"]

     if password != admin_password:
          return response.forbidden_response(message="incorrect password")

     session_token = generate_unique_token()
     database.update_admin_token(email=email, session_token=session_token)

     return response.successful_response(data={ "email": email, "session_token": session_token })

@router.get("/create_admin/")
def create_admin(email: str, password: str, site_key: str):
     if SITE_KEY != site_key:
          return response.forbidden_response(message="site_key is invalid")

     if len(password) < 10:
          return response.bad_request_response(message="password should have atleast 10 characters")

     db_response = database.create_admin(email=email, password=password)
     
     if not db_response:
          return response.crash_response()

     return response.successful_response()

@router.get("/upload_project/{repo_slug}")
def upload(email: str, repo_slug: str, images: str):
     if images == "":
          return response.bad_request_response(message="no images")

     image_urls = upload_images(string_images=images)

     if not image_urls:
          return response.crash_response(message="something went wrong with uploading the images")

     db_response = database.upload_project(repo_slug, images=image_urls)

     if not db_response:
          return response.crash_response(message="something went wrong with uploading the project")
     
     session_token = generate_unique_token()
     database.update_admin_token(email=email, session_token=session_token)
     
     return response.successful_response(data={ "session_token": session_token })

@router.get("/edit_project/{repo_slug}")
def edit(email: str, repo_slug: str, images: str):
     project = database.get_project(repo_slug)

     if not project:
          return response.not_found_response(message="project not found") 

     project_images = project["images"]
     new_project_images = process_project_images(images=images, project_images=project_images)

     db_response = database.update_images(images=new_project_images)

     if not db_response:
          return response.crash_response(message="something went wrong with trying to update images")

     session_token = generate_unique_token()
     database.update_admin_token(email=email, session_token=session_token)
     
     return response.successful_response(data={ "session_token": session_token })
     
@router.get("/delete_project/{repo_slug}")
def delete_project(email: str, repo_slug: str):
     project = database.get_project(repo_slug)

     if not project:
          return response.not_found_response(message="project not found") 

     db_response = database.delete_project(repo_slug)

     if not db_response:
          return response.crash_response(message="something went wrong with trying to delete project")

     session_token = generate_unique_token()
     database.update_admin_token(email=email, session_token=session_token)
     
     return response.successful_response(data={ "session_token": session_token })
     



def upload_images(string_images: str) -> Optional[List[str]]:
     return None