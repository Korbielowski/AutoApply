import uvicorn
from .backend.app_setup import app


def main() -> None:
    pass


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port="8000")
