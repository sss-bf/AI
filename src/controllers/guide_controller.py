from typing import Optional
from fastapi import APIRouter, HTTPException
from src.models.test_ai_model import TestAIModel
import os
from src.models.open_ai_model import OpenAIModel

class GuideController:
    def __init__(self):
        self.router = APIRouter(prefix="/api", tags=["Guides"])
        self.router.add_api_route("/v1/guide", self.create_guide, methods=["POST"])
        self.router.add_api_route("/v2/guide", self.create_guide2, methods=["POST"])

    def create_guide(self, user_request: str, image_url: str):
        guide_text = ""
        guide_image_url = ""

        openai_api_key = os.getenv("OPENAI_API_KEY")
        ai_model = TestAIModel(openai_api_key)

        # TODO: 프롬프트 생성 필요
        prompt = user_request

        # guide_text, guide_image_url = ai_model.request(prompt, image_url)
        guide_text, guide_image_url = ai_model.test_request(prompt), image_url

        # guide_text, guide_image_url = user_request, image_url

        return {"guideText": guide_text, "guideImageUrl": image_url}
    
    def create_guide2(self, user_request: Optional[str] = None, image_url: Optional[str] = None):
        if (user_request is None or user_request == "") and (image_url is None or image_url == ""):
            raise HTTPException(status_code=400, detail="Parameters are required at least one or both of them")
            
        guide_text = ""
        guide_image_url = ""

        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model = OpenAIModel(openai_api_key)

        prompt = user_request

        guide_text = self.model.request(image_url, prompt)

        return {"guideText": guide_text, "guideImageUrl": image_url}
