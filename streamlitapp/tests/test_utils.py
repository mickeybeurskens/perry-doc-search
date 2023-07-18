import pytest
import pydantic
import tempfile
from perry.utils import *


class TestModel(pydantic.BaseModel):
    name: str
    age: int


def test_save_should_output_json_file():
    """ Saving a pydantic model should create a json file. """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = pathlib.Path(tmp_dir)
        model = TestModel(name="John", age=42)
        save_pydantic_instance(model, tmp_dir / "test.pickle")
        assert (tmp_dir / "test.pickle").exists()


def test_load_should_equal_save():
    """ Loading a pydantic model should equal the original model. """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = pathlib.Path(tmp_dir)
        model = TestModel(name="John", age=42)
        save_pydantic_instance(model, tmp_dir / "test.pickle")
        loaded_model = load_pydantic_instance(TestModel, tmp_dir / "test.pickle")
        assert model == loaded_model


def test_load_openai_api_key_should_load_env_file():
    """ Loading OpenAI API key should load from environment variable. """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = pathlib.Path(tmp_dir)
        file_path = tmp_dir / ".env"
        with open(file_path, "w") as f:
            f.write("OPENAI_API_KEY=12345")
        load_openai_api_key(file_path)
        assert openai.api_key == "12345"


def test_get_production_env_path_should_return_path():
    """ get_production_env_path should return the path to the production env file. """
    path = get_production_env_path()
    assert path.exists()
    assert path.parent.name == "streamlitapp"


def test_load_openai_api_key_should_error_if_key_not_exists():
    """ Loading OpenAI API key should error if environment variable does not exist. """
    openai.api_key = ""
    test_key = "OPENAI_API_KEY_TEST_2"
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = pathlib.Path(tmp_dir)
        file_path = tmp_dir / ".env"
        with open(file_path, "w") as f:
            with pytest.raises(ValueError):
                load_openai_api_key(file_path, test_key)
            f.write(f"{test_key}=")
        with pytest.raises(ValueError):
            load_openai_api_key(file_path, test_key)


def test_load_openai_api_key_should_error_if_env_file_not_exists():
    """ Loading OpenAI API key should error if environment variable does not exist. """
    openai.api_key = ""
    test_key = "OPENAI_API_KEY_TEST"
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = pathlib.Path(tmp_dir)
        file_path = tmp_dir / ".env"
        with pytest.raises(FileNotFoundError):
            load_openai_api_key(file_path, test_key)


def test_get_file_paths_should_only_show_files():
    """ get_file_paths should only return files one deep, not directories. """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = pathlib.Path(tmp_dir)
        (tmp_dir / "file1.txt").touch()
        (tmp_dir / "file2.txt").touch()
        (tmp_dir / "file3.txt").touch()
        (tmp_dir / "dir").mkdir()
        (tmp_dir / "dir" / "file4.txt").touch()
        (tmp_dir / "dir" / "file5.txt").touch()
        (tmp_dir / "dir" / "file6.txt").touch()
        file_paths = get_file_paths_from_dir(tmp_dir)
        assert len(file_paths) == 3
        assert all([path.is_file() for path in file_paths])
