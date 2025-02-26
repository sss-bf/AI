from fastapi import APIRouter
from src.models.test_ai_model import AIModel
import os

class GuideController:
    def __init__(self):
        self.router = APIRouter(prefix="/api/v1/guide", tags=["Guides"])
        self.router.add_api_route("/", self.create_guide, methods=["POST"])

    def create_guide(self, user_request: str, image_url: str):
        guide_text: str = ""
        guide_image_url = ""

        openai_api_key = os.getenv("OPENAI_API_KEY")
        ai_model = AIModel(openai_api_key)

        # TODO: 프롬프트 생성 필요
        prompt = user_request

        # guide_text, guide_image_url = ai_model.request(prompt, image_url)
        guide_text, guide_image_url = ai_model.test_request(prompt), image_url

        # guide_text, guide_image_url = user_request, image_url

        return {"guideText": f"AI Model Response : [{guide_text}]", "guideImageUrl": f"AI Model Response : [{image_url}]"}
