import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import pathlib
import os


def get_config_directory_path():
    return pathlib.Path(__file__).parent.parent.absolute() / 'config'


def get_prodution_config_path():
    path = get_config_directory_path() / 'production.yml'
    if not path.exists():
        raise FileNotFoundError(f'Production config file not found at {path}')
    return path


def get_development_config_path():
    path = get_config_directory_path() / 'development.yml'
    if not path.exists():
        raise FileNotFoundError(f'Development config file not found at {path}')
    return path


def load_config(path):
    with open(path) as file:
        return yaml.load(file, Loader=SafeLoader)
    

def get_authentication_config() -> stauth.Authenticate:
    development = os.environ.get('PERRY_DEPLOYMENT_MODE', 'production') == 'development'
    if development:
        conf_yml = load_config(get_development_config_path())
    else:
        conf_yml = load_config(get_prodution_config_path())
    return stauth.Authenticate(
        conf_yml['credentials'],
        conf_yml['cookie']['name'],
        conf_yml['cookie']['key'],
        conf_yml['cookie']['expiry_days'],
        conf_yml['preauthorized']
    )