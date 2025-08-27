from pydantic import Field
from pydantic_settings import BaseSettings
import fsspec

class Settings(BaseSettings):
    MBX_DATA_URI: str = Field('file://./_mbxdata', description='Base URI for data lake')

settings = Settings()

def resolve_path(subpath: str) -> str:
    return f"{settings.MBX_DATA_URI.rstrip('/')}/{subpath.lstrip('/')}"

def open_file(subpath: str, mode: str='rb'):
    return fsspec.open(resolve_path(subpath), mode).open()
