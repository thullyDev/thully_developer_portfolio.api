import json
from typing import Any, Dict
from fastapi.responses import JSONResponse
from ..resources import (
    FORBIDDEN, 
    CRASH, 
    SUCCESSFUL, 
    NOT_FOUND, 
    FORBIDDEN_MSG, 
    CRASH_MSG, 
    SUCCESSFUL_MSG, 
    NOT_FOUND_MSG, 
    BAD_REQUEST, 
    BAD_REQUEST_MSG
)

def json_response(status_code: int, data: Dict[str, Any]) -> JSONResponse:
    return JSONResponse(content=data, status_code=status_code)

def create_context(data: Dict[str, Any], status_code: int, message: str) -> Dict[str, Any]:
    return {
        "message": message,
        "status_code": status_code,
        "data": data,
    }

def forbidden_response(data: Dict[str, Any] = {}, status_code: int = FORBIDDEN, message: str = FORBIDDEN_MSG) -> JSONResponse:
    data = create_context(data, status_code, message)
    return json_response(status_code=FORBIDDEN, data=data)

def successful_response(data: Dict[str, Any] = {}, status_code: int = SUCCESSFUL, message: str = SUCCESSFUL_MSG) -> JSONResponse:
    data = create_context(data, status_code, message)
    return json_response(status_code=SUCCESSFUL, data=data)

def not_found_response(data: Dict[str, Any] = {}, status_code: int = NOT_FOUND, message: str = NOT_FOUND_MSG) -> JSONResponse:
    data = create_context(data, status_code, message)
    return json_response(status_code=NOT_FOUND, data=data)

def crash_response(data: Dict[str, Any] = {}, status_code: int = CRASH, message: str = CRASH_MSG) -> JSONResponse:
    data = create_context(data, status_code, message)
    return json_response(status_code=CRASH, data=data)

def bad_request_response(data: Dict[str, Any] = {}, status_code: int = BAD_REQUEST, message: str = BAD_REQUEST_MSG) -> JSONResponse:
    data = create_context(data, status_code, message)
    return json_response(status_code=BAD_REQUEST, data=data)
