# from models import Profile
# from functools import wraps
from typing import Callable

# from fastapi import Request
from fastapi.responses import RedirectResponse
from backend.app_setup import profile

DB_NAME = ""


def authenticate_user(func: Callable) -> Callable:
    # @wraps(func)
    def wrapper(func):
        if not profile:
            return RedirectResponse(url="/login")
        # return func

    return wrapper
