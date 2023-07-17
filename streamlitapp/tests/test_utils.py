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
        save_pydantic_instance(model, tmp_dir / "test.json")
        assert (tmp_dir / "test.json").exists()


def test_load_should_equal_save():
    """ Loading a pydantic model should equal the original model. """
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = pathlib.Path(tmp_dir)
        model = TestModel(name="John", age=42)
        save_pydantic_instance(model, tmp_dir / "test.json")
        loaded_model = load_pydantic_instance(TestModel, tmp_dir / "test.json")
        assert model == loaded_model
