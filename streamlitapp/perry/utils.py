import os
import pickle
import openai
import pathlib
import pydantic
from dotenv import load_dotenv


def save_pydantic_instance(model_instance: pydantic.BaseModel, path: pathlib.Path) -> None:
    """ Save a pydantic instance to a json file. 
    args:
        model_instance: pydantic instance to save
        path: pathlib.Path to save the instance to
    """
    with open(path, "wb") as f:
        f.write(pickle.dumps(model_instance.dict()))


def load_pydantic_instance(model_class: pydantic.BaseModel, path: pathlib.Path) -> pydantic.BaseModel:
    """ Load a pydantic instance from a json file. 
    args:
        model_class: pydantic class to load, not the instance
        path: pathlib.Path to load the instance from
    """
    if isinstance(model_class, pydantic.BaseModel):
        raise ValueError("model_class must be an uninstanciated pydantic class.")
    with open(path, "rb") as f:
        pickle_data = f.read()
    instance = model_class.parse_raw(
        pickle_data, content_type='application/pickle', allow_pickle=True)   
    return instance


def load_openai_api_key(file_path: pathlib.Path, key: str = "OPENAI_API_KEY") -> None:
    """Load OpenAI API key from environment variable."""
    if not openai.api_key:
        if not file_path.exists():
            raise FileNotFoundError(f"Could not find .env file at {file_path}")
        load_dotenv(dotenv_path=file_path)
        if key not in os.environ:
            raise ValueError(f"{key} environment variable not found in {file_path}")
        if os.environ[key] == "":
            raise ValueError(f"{key} environment variable is empty in {file_path}")
        openai.api_key = os.environ[key]


def get_production_env_path() -> pathlib.Path:
    """Get path to production environment file."""
    return pathlib.Path(__file__).parent.parent / ".env"


def get_file_paths_from_dir(data_dir: pathlib.Path) -> list[pathlib.Path]:
    """Get file paths of files in a directory."""
    return [f for f in data_dir.iterdir() if f.is_file()]