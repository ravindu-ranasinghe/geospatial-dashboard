from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    data_url: str = (
        "https://opendata.arcgis.com/api/v3/datasets/"
        "441d4c0410854e3da692b24347ab6b0d_0/downloads/data"
        "?format=csv&spatialRefId=4326"
    )
    cache_dir: str = "data"
    data_limit: int = 2000
    map_center_lat: float = 44.9778
    map_center_lon: float = -93.2650
    map_zoom: int = 12

    model_config = {"env_prefix": "GEOINT_"}


settings = Settings()
