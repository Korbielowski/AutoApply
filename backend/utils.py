# from models import Profile
# from functools import wraps
from typing import Callable

# from fastapi import Request
from fastapi.responses import RedirectResponse

DB_NAME = ""


def authenticate_user(func: Callable) -> Callable:
    # @wraps(func)
    def wrapper(func):
        return RedirectResponse(url="/prison")
        # return func

    return wrapper
