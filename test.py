import openai
import base64
import requests
from PIL import Image
from io import BytesIO
import os

from dotenv import load_dotenv

# OpenAI API Key 설정

load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI 클라이언트 인스턴스 생성
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def encode_image_to_base64(image_path):
    """이미지를 Base64로 변환"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image_and_generate_prompt(image_path, user_background_request):
    """
    1. GPT-4o에게 이미지를 직접 보내서 메인 객체 분석 (Base64 방식)
    2. 사용자가 원하는 배경 스타일을 반영한 DALL·E 3 프롬프트 생성
    """
    # 이미지를 Base64로 인코딩
    base64_image = encode_image_to_base64(image_path)

    # GPT-4o에게 이미지와 함께 요청
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an AI assistant that analyzes images and generates photorealistic prompts for DALL·E 3."},
            {"role": "user", "content": [
                {"type": "text", "text": f"Analyze this image and identify the main object. The user wants to change the background to: '{user_background_request}'. Generate a detailed photorealistic prompt for DALL·E 3 while preserving the main object."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ],
        max_tokens=500
    )

    # GPT-4o가 생성한 프롬프트 가져오기
    gpt_generated_prompt = response.choices[0].message.content
    print("🔹 GPT-4o가 생성한 초기 프롬프트:", gpt_generated_prompt)

    # 최적화된 DALL·E 3 프롬프트
    final_prompt = f"""
    Generate an image where the main object remains completely unaltered, preserving its original shape, color, texture, and details exactly as in the provided image.

    Only modify the background to match the following setting: {user_background_request}. The transition between the object and the new background must be seamless, ensuring natural lighting, depth of field, and realistic shadows.

    Maintain a photorealistic quality to make the final image appear as if it was captured in the real world, with natural reflections and high-resolution textures.
    """

    print("🔹 최종 DALL·E 3 프롬프트:", final_prompt)
    return final_prompt

def generate_new_image_with_dalle(prompt):
    """
    DALL·E 3를 사용하여 배경만 변경된 이미지 생성
    """
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
    )

    image_url = response.data[0].url
    print(f"🖼️ 생성된 이미지 URL: {image_url}")

    # 이미지 다운로드 및 표시
    image_response = requests.get(image_url)
    img = Image.open(BytesIO(image_response.content))
    img.show()

    return image_url

# 🔹 실행 예시
image_path = "./result_histories/20250228-012748.jpg"  # 로컬 이미지 경로
user_background_request = "A futuristic cyberpunk city with neon lights at night"

# 1️⃣ GPT-4o로 프롬프트 생성
optimized_prompt = analyze_image_and_generate_prompt(image_path, user_background_request)

# 2️⃣ DALL·E 3로 새로운 이미지 생성
new_image_url = generate_new_image_with_dalle(optimized_prompt)
