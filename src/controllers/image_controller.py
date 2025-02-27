from fastapi import APIRouter, HTTPException
import os
from fastapi.responses import FileResponse

class ImageController:
    def __init__(self):
        self.router = APIRouter(prefix="/api", tags=["Images"])
        self.router.add_api_route("/v1/images/{file_name}", self.get_image, methods=["GET"])

    def get_image(self, file_name: str):
        file_path = os.path.join("./result_histories", file_name)
        print(file_path)
        if os.path.exists(file_path):
            return FileResponse(file_path)
        else:
            raise HTTPException(status_code=404, detail=f"File not found (File Name : {file_name})")
