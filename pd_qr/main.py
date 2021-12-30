import json
import os
from pathlib import Path

import uvicorn
from decouple import config
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.openapi.utils import get_openapi
from models import get_unprocessed_qr_frame_url
from qr_code import qr_to_text

base_path = os.path.dirname(os.path.abspath(__file__))


app = FastAPI()


@app.post("/perform_qr_code_to_text", status_code=200, tags=["Qr Code"])
async def perform_qr_code_to_text(background_tasks: BackgroundTasks, request: Request):
    data = await request.json()
    # image_path = data['image_url']
    video_id = data["video_id"]
    frame_id = data["frame_id"]
    input_data = {"id": frame_id, "video_id": video_id}
    image_path = await get_unprocessed_qr_frame_url(input_data)
    try:
        if not image_path or len(image_path.strip()) == 0:
            raise HTTPException(
                status_code=404, detail="image path is invalid or empty"
            )
        else:
            background_tasks.add_task(qr_to_text, image_path, frame_id, video_id)
        print({"video_id": video_id, "frame_id": frame_id, "image_path": image_path})
        return {
            "response": "soon the predictions will be compeleted",
            "file_name": image_path,
        }
    except:
        print("image not processed for some reason")


tags_metadata = [
    {
        "name": "decord",
        "description": "This End point used to extract the text information form QR Code",
    }
]

description = """
QR Code API 🚀
"""


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Point Duty - QR Code API",
        version="V-0.0.0",
        description=description,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    app.openapi_tags = tags_metadata
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    # $ uvicorn main:app --reload
    port = config("FASTAPI_LOCAL_PORT", cast=int)
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload="True")
