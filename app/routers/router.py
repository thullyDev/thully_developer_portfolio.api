from typing import Any, List, Optional, Dict
from typing_extensions import Tuple
from fastapi import APIRouter
from app.handlers import response_handler as response
from app.database import database
from app.resources.config import SITE_KEY
from app.resources.misc import generate_unique_token
from app.handlers import storage
import datetime
import json

router: APIRouter = APIRouter(prefix="/api")

@router.get("/update_site_data/")
def update_site_data(email: str, dataStr: str):
     data = json.loads(dataStr)
     images: List[str] = process_upload_profile_images(data["images"])
     data["images"] = images
     db_response = database.update_site_data(data)

     if not db_response:
          return response.crash_response(message="something went with updating the site data")

     session_token = generate_unique_token()
     database.update_admin_token(email=email, session_token=session_token)
     
     return response.successful_response(data={ "session_token": session_token })


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
def upload_project(email: str, repo_slug: str, images: str):
     if images == "":
          return response.bad_request_response(message="no images")

     image_urls = upload_images(string_images=images, repo_slug=repo_slug)

     db_response = database.upload_project(repo_slug, images=image_urls)

     if not db_response:
          return response.crash_response(message="something went wrong with uploading the project")
     
     session_token = generate_unique_token()
     database.update_admin_token(email=email, session_token=session_token)
     
     return response.successful_response(data={ "session_token": session_token })

@router.get("/get_project/{repo_slug}")
def get_project(email: str, repo_slug: str):
     project = database.get_project(repo_slug)

     if not project:
          return response.not_found_response(message="project not found") 

     del project["_id"]

     session_token = generate_unique_token()
     database.update_admin_token(email=email, session_token=session_token)
     
     return response.successful_response(data={ "project": project, "session_token": session_token })

@router.get("/edit_project/{repo_slug}")
def edit_project(email: str, repo_slug: str, images: str):
     project = database.get_project(repo_slug)

     if not project:
          return response.not_found_response(message="project not found") 

     new_project_images = upload_images(string_images=images, repo_slug=repo_slug)
     db_response = database.update_project_images(images=new_project_images, repo_slug=repo_slug)

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
     
def process_upload_profile_images(profile_images: Dict[str, str]) -> List[str]:
     image_urls = []

     for key, image in profile_images.items():
          if "https://" in image: 
               # this condition is here for when its used in the edit, 
               # it checks if the image from the image storage, 
               # if so then it then it just appends it and moves on
               image_urls.append(image)
               continue

          name, base64image = process_image(image=image, name=f"profile-image-{key}") 
          image_url = storage.upload_base64_image(name=name, base64Str=base64image)
          image_urls.append(image_url)

     return image_urls

def upload_images(string_images: str, repo_slug: str) -> List[str]:
     spliter = "---***---" # never change this, it will conflict with the frontend
     base64images = string_images.split(spliter) 
     image_urls = []

     for index, image in enumerate(base64images):

          if "https://" in image: 
               # this condition is here for when its used in the edit, 
               # it checks if the image from the image storage, 
               # if so then it then it just appends it and moves on
               image_urls.append(image)
               continue

          name, base64image = process_image(image=image, name=f"{repo_slug}-image-{index}") 
          image_url = storage.upload_base64_image(name=name, base64Str=base64image)
          image_urls.append(image_url)

     return image_urls

def process_image(image: str, name: str) -> Tuple[str, str]:
     current_time = datetime.datetime.now().strftime("%d-%m-%Y-%w-%d-%H-%M-%S-%f")
     name = f"{name}-{current_time}"

     return name, image.replace("data:image/jpeg;base64,", "").replace("data:image/png;base64,", "")

