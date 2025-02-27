import requests
from PIL import Image
from io import BytesIO
from datetime import datetime
import os
from fastapi import Request
from src.utils.datetime_helper import CurrentDateTime

class ImageFileHelper:
    def __init__(self):
        pass

    def get_image_from_url(self, image_url: str):
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
        return image

    def save_image_from_url(self, image_url: str, file_name: str = None, base_directory: str = None):
        _, extension = os.path.splitext(image_url)

        print(f"Loading Image - {image_url}")
        response = requests.get(image_url)
        print("reponded")
        image = Image.open(BytesIO(response.content))
        print("open Image")

        if file_name is None or file_name == "":
            file_name = f"{CurrentDateTime()}{extension}"

        if base_directory is None or base_directory == "":
            base_directory = "./result_histories"

        image_file = os.path.join(base_directory, file_name)
        image.thumbnail((300, 300))
        image.save(image_file, image.format)
        return image_file

    def save_pil_image(image: Image, file_extension: str, base_directory: str = None):
        
        if file_name is None or file_name == "":
            file_name = f"{str(datetime.now().strftime("%Y%m%d-%H%M%S"))}{file_extension}"

        if base_directory is None or base_directory == "":
            base_directory = "./result_histories"

        image.save(os.path.join(base_directory, file_name), image.format)

    def get_url_from_image(self, request: Request, image_file_name: str):
        return os.path.join(request.base_url._url, "api/v1/images", image_file_name)

if __name__ == "__main__":
    imageFileHelper = ImageFileHelper()
    imageFileHelper.save_image_from_url("http://localhost:8000/api/v1/images/rainbow.jpg")
