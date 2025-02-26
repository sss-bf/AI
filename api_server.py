from fastapi import FastAPI
from fastapi.responses import FileResponse
from test_ai_model import AIModel

app = FastAPI()

@app.get("/api/v1/guide")
def GetGuide(query: str, image_url: str):
    guide_text: str = ""
    guide_image_url = ""

    ai_model = AIModel()

    guide_text, guide_image_url = ai_model.request(query, image_url)

    return {"guideText": guide_text, "guideImageUrl": guide_image_url}
