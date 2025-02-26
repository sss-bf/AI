from fastapi import FastAPI
from fastapi.responses import FileResponse
from test_ai_model import AIModel

app = FastAPI()

@app.post("/api/v1/guide")
def GetGuide(user_request: str, image_url: str):
    guide_text: str = ""
    guide_image_url = ""

    ai_model = AIModel()

    # TODO: 프롬프트 생성 필요
    prompt = user_request

    # guide_text, guide_image_url = ai_model.request(prompt, image_url)
    # guide_text, guide_image_url = ai_model.test_request(prompt), image_url

    guide_text, guide_image_url = user_request, image_url

    return {"guideText": f"AI Model Response : [{guide_text}]", "guideImageUrl": f"AI Model Response : [{image_url}]"}
