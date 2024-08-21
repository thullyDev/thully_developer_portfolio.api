from typing import Any, List, Optional, Dict
from requests import session
from typing_extensions import Tuple
from fastapi import APIRouter, Request
from app.handlers import response_handler as response
from app.database import database
from app.resources.config import SITE_KEY
from app.resources.misc import generate_unique_token
from app.handlers import storage
from urllib.parse import parse_qs, urlparse
import datetime
import json

router: APIRouter = APIRouter(prefix="/api")

async def validator(*, request: Request, callnext):
     url = request.url._url
     url_chunks = url.split("/")

     if("login" in url_chunks \
        or "create_admin" in url_chunks \
        or "get_site_data" in url_chunks \
        or "get_project" in url_chunks): 
          return await callnext(request)


     headers = request.headers
     session_token = headers.get("session_token")

     if not session_token:
          return response.forbidden_response(data={ "message": "bad session_token" })


     email = None
     method = request.method

     if "POST" == method:
          email = headers.get("email") 

     if "GET" == method:
          email = get_email_from_url_req(url)


     if not email:
          return response.bad_request_response()

     admin = database.get_admin(email)
     
     if not admin:
          return response.forbidden_response(data={ "message": "invalid admin"})


     if admin["session_token"] != session_token:
          return response.forbidden_response(data={ "message": "admin not up to date with the session_token, so they should authenticate first"})
     
     session_token = generate_unique_token()
     database.update_admin_token(email=email, session_token=session_token)

     request.state.session_token = session_token

     return await callnext(request)



from pprint import pprint

@router.post("/update_site_data/")
def update_site_data(request: Request, dataStr: str):
     data = json.loads(dataStr)
     images: Dict[str, str] = process_upload_profile_images(data["images"])
     data["images"] = images

     db_response = database.update_site_data(data)

     if db_response == False:
          db_response = database.set_site_data(data)

     if not db_response:
          return response.crash_response(message="something went with updating the site data")

     return response.successful_response(data={ "session_token": request.state.session_token  })

@router.get("/get_site_data/")
def get_site_data():
     data = database.get_site_data()

     if data:
          del data["_id"]

     return response.successful_response(data={ "site_data": data.get("data") })


@router.post("/login/")
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

@router.post("/upload_project/{repo_slug}")
def upload_project(request: Request, repo_slug: str, images: str):
     if images == "":
          return response.bad_request_response(message="no images")

     image_urls = upload_images(string_images=images, repo_slug=repo_slug)

     db_response = database.upload_project(repo_slug, images=image_urls)

     if not db_response:
          return response.crash_response(message="something went wrong with uploading the project")
     
     return response.successful_response(data={ "session_token": request.state.session_token })

@router.get("/get_project/{repo_slug}")
def get_project(repo_slug: str):
     project = database.get_project(repo_slug)

     if not project:
          return response.not_found_response(message="project not found") 

     del project["_id"]
     
     return response.successful_response(data={ "project": project })

@router.post("/edit_project/{repo_slug}")
def edit_project(request: Request, repo_slug: str, images: str):
     project = database.get_project(repo_slug)

     if not project:
          return response.not_found_response(message="project not found") 

     new_project_images = upload_images(string_images=images, repo_slug=repo_slug)
     db_response = database.update_project_images(images=new_project_images, repo_slug=repo_slug)

     if not db_response:
          return response.crash_response(message="something went wrong with trying to update images")
     
     return response.successful_response(data={ "session_token": request.state.session_token })
     
@router.post("/delete_project/{repo_slug}")
def delete_project(request: Request, repo_slug: str):
     project = database.get_project(repo_slug)

     if not project:
          return response.not_found_response(message="project not found") 

     db_response = database.delete_project(repo_slug)

     if not db_response:
          return response.crash_response(message="something went wrong with trying to delete project")
     
     return response.successful_response(data={ "session_token": request.state.session_token })
     
def process_upload_profile_images(profile_images: Dict[str, str]) -> Dict[str, str]:
     images: Any = {}

     for key, image in profile_images.items():
          if "https://" in image: 
               # this condition is here for when its used in the edit, 
               # it checks if the image from the image storage, 
               # if so then it then it just appends it and moves on
               images[key] = image
               continue

          name, base64image = process_image(image=image, name=f"profile-image-{key}") 
          image_url = storage.upload_base64_image(name=name, base64Str=base64image)
          images[key] = image_url

     return images

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


def get_email_from_url_req(url) -> Optional[str]:
     parsed_url = urlparse(url)
     query_params = parse_qs(parsed_url.query)
     email = query_params.get('email', [None])[0]

     return email