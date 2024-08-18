from fastapi import FastAPI, Request
from .routers import router 
from fastapi.responses import JSONResponse
from app.handlers import response_handler as response
from app.resources.config import ORIGINS 
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
origins = ORIGINS.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type", "session_token"],
)

def middleware(request: Request, callnext):
    url_path = request.url.path
    temp = url_path.split("/")

    if "api" in temp:
        return router.validator(request=request, callnext=callnext) 

    return callnext(request)

app.middleware("http")(middleware)

@app.exception_handler(Exception)
def unexpected_error_handler() -> JSONResponse:
    return response.crash_response(data={ "message": "Unexpected error occurred" })

@app.get("/")
def root() -> JSONResponse:
    return response.successful_response(data={ "message": f"server is running... follow me on https://github.com/thullDev" })

app.include_router(router.router)

