import json
from re import sub

import aiohttp
import requests
from decouple import config
from fastapi.responses import JSONResponse

ip_address = config("MY_IP")


async def send_massage_to_server(massage):
    params = {"massage": json.dumps(massage)}
    print(params)
    api_end_point = f"http://{ip_address}:8000/simple_massage_service"
    requests.get(api_end_point, params=params)


async def snake_case(s):
    return "_".join(sub("([A-Z][a-z]+)", r" \1", sub("([A-Z]+)", r" \1", s.replace("-", " "))).split()).lower()
