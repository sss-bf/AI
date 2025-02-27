from fastapi import APIRouter, HTTPException, Request
from src.models.test_ai_model import TestAIModel
from src.models.open_ai_model import OpenAIModel
import os

class GuideController:
    def __init__(self):
        self.router = APIRouter(prefix="/api", tags=["Guides"])
        self.router.add_api_route("/v1/guide", self.create_guide, methods=["POST"])
        self.router.add_api_route("/test/guide", self.create_guide_test, methods=["POST"])

    def create_guide(self, user_request: str = None, image_url: str = None):
        if (user_request is None or user_request == "") and (image_url is None or image_url == ""):
            raise HTTPException(status_code=400, detail="Parameters are required at least one or both of them")

        if self.model == None:
            self.model = OpenAIModel()

        # TODO: Optimize Prompt
        prompt = user_request

        # TODO: request will return guide_image_url also
        guide_text, guide_image_url = self.model.request(image_url, prompt), image_url

        return {"guideText": guide_text, "guideImageUrl": guide_image_url}

    def create_guide_test(self, request: Request, user_request: str, image_url: str):
        guide_text = ""
        guide_image_url = ""

        ai_model = TestAIModel()

        # prompt = user_request
        # guide_text, guide_image_url = ai_model.request(prompt)

        image_name = "rainbow.jpg"
        new_image_url = os.path.join(request.base_url._url, "api/v1/images", image_name)
        
        return {"guideText": user_request, "guideImageUrl": new_image_url}
