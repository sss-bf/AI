
import requests

# 🔹 ImgBB API 키 (ImgBB에서 회원가입 후 API 키 발급 필요)
API_KEY = "31df178da1c48f1036cd568e09690c07"

# 🔹 업로드할 이미지 파일 경로
IMAGE_PATH = "./result_histories/rainbow.jpg"

# 🔹 API 요청 URL
UPLOAD_URL = "https://api.imgbb.com/1/upload"

# 🔹 이미지 업로드 요청
with open(IMAGE_PATH, "rb") as file:
    response = requests.post(UPLOAD_URL, data={"key": API_KEY}, files={"image": file})

# 🔹 응답 결과 확인
if response.status_code == 200:
    result = response.json()
    image_url = result["data"]["url"]
    print(f"✅ 이미지 업로드 성공! URL: {image_url}")
else:
    print(f"❌ 업로드 실패! 오류 코드: {response.status_code}, 메시지: {response.text}")
