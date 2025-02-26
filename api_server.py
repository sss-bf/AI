from typing import Union

from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/test")
def read_root(item: str):
    return {"result": "item"}


@app.get("/api/v1/guide")
def GetGuide(query: str, image_url: str):
    guide_text: str = ""
    guide_image = None

    # TODO: GPT API Call & result 생성 및 반환

    return {"guideText": guide_text, "guideImage": guide_image}

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"./{filename}"
    return FileResponse(file_path, media_type="image/jpeg", filename=filename)
