from fastapi import APIRouter, HTTPException
from src.models.open_ai_model import OpenAIModel

class GuideController:
    def __init__(self):
        self.router = APIRouter(prefix="/api", tags=["Guides"])
        self.router.add_api_route("/v1/guide", self.create_guide, methods=["POST"])
        self.model = None

    def create_guide(self, user_request: str = None, image_url: str = None):
        if (user_request is None or user_request == "") and (image_url is None or image_url == ""):
            raise HTTPException(status_code=400, detail="Parameters are required at least one or both of them")

        if self.model == None:
            self.model = OpenAIModel()

        # TODO: request will return guide_image_url also
        guide_text, guide_image_url = self.model.request(image_url, user_request)

        return {"guideText": guide_text, "guideImageUrl": guide_image_url}
