from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import shutil
import os
from uuid import uuid4
from model import process_photo_feedback, update_photo_feedback

app = FastAPI()  # ✅ FastAPI 객체 선언

@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}


# 업로드된 이미지 저장 경로
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 사진 업로드 및 피드백 요청 처리
@app.post("/upload/")
async def upload_photo(file: UploadFile = File(...), user_preference: str = Form(...)):
    """
    사용자가 사진을 업로드하면, 서버에 저장하고 URL을 반환하여
    LangGraph 모델에 전달 후 피드백을 제공한다.
    """
    # 파일 저장 경로 설정
    file_ext = file.filename.split(".")[-1]
    file_name = f"{uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    # 파일 저장
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 업로드된 파일의 URL 생성 (로컬 서버 기준)
    image_url = f"http://127.0.0.1:8000/uploads/{file_name}"

    # LangChain 모델을 통해 피드백 생성
    feedback = process_photo_feedback(image_url, user_preference)

    return JSONResponse(content={"image_url": image_url, "feedback": feedback})

@app.post("/upload/new/")
async def upload_new_photo(file: UploadFile = File(...), user_preference: str = Form(...), old_feedback: str = Form(...)):
    """
    사용자가 새로운 사진을 업로드하면 기존 피드백을 반영하여 평가하고 새로운 피드백을 제공한다.
    """
    # 파일 저장 경로 설정
    file_ext = file.filename.split(".")[-1]
    file_name = f"{uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    # 파일 저장
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 업로드된 파일의 URL 생성 (로컬 서버 기준)
    new_image_url = f"http://127.0.0.1:8000/uploads/{file_name}"

    # LangChain 모델을 통해 새로운 피드백 생성
    new_feedback = update_photo_feedback(new_image_url, user_preference, old_feedback)

    return JSONResponse(content={"new_image_url": new_image_url, "feedback": new_feedback})

# 업로드된 이미지 접근 라우트
from fastapi.staticfiles import StaticFiles
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")