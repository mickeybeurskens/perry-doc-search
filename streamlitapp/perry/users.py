import pydantic
import pathlib


class User(pydantic.BaseModel):
    name: str
    username: str
    email: pydantic.EmailStr
    hashed_password = str


def get_user_save_dir() -> pathlib.Path:
    """Return the default user save directory."""
    path = pathlib.Path(__file__).parent.parent / "storage" / "users"
    if not path.exists():
        path.mkdir(parents=True)
    return path
