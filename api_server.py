from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from src.controllers.guide_controller import GuideController
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
app.include_router(GuideController().router)

# 개발 환경에서 Root Path 접속 시, swagger 페이지로 Redirect
@app.get("/")
async def root():
    env = os.getenv("ENVIRONMENT")
    if(env == "dev"):
        return RedirectResponse(url="/docs")
    else:
        return HTTPException(status_code=404)
