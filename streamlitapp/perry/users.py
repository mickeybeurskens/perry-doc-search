import pydantic
import pathlib
from perry.utils import save_pydantic_instance, load_pydantic_instance


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


def save_user(user: User, path: pathlib.Path) -> None:
    """Save a user to a json file."""
    file_name = f"user_{user.username}.json"
    file_path = path / file_name
    save_pydantic_instance(user, file_path)


def load_user(username: str, path: pathlib.Path) -> User:
    """Load a user from a json file."""
    file_name = f"user_{username}.json"
    file_path = path / file_name
    user = load_pydantic_instance(User, file_path)
    return user
