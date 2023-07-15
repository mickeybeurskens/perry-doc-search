import pydantic
import pathlib
import json


def save_pydantic_instance(model_instance: pydantic.BaseModel, path: pathlib.Path) -> None:
    """ Save a pydantic instance to a json file. 
    args:
        model_instance: pydantic instance to save
        path: pathlib.Path to save the instance to
    """
    with open(path, "w") as f:
        json.dump(model_instance.model_dump(mode='json'), f, indent=2)


def load_pydantic_instance(model_class: pydantic.BaseModel, path: pathlib.Path) -> pydantic.BaseModel:
    """ Load a pydantic instance from a json file. 
    args:
        model_class: pydantic class to load, not the instance
        path: pathlib.Path to load the instance from
    """
    if isinstance(model_class, pydantic.BaseModel):
        raise ValueError("model_class must be an uninstanciated pydantic class.")
    with open(path, "r") as f:
        message_history = model_class(**json.load(f))
    return message_history