from fastapi import APIRouter
import openai
# from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
import requests
from PIL import Image
from io import BytesIO
import os
from langchain_community.chat_models import ChatOpenAI


class TestController:
    def __init__(self):
        self.router = APIRouter(prefix="/api", tags=["Tests"])
        self.router.add_api_route("/v1/test", self.test, methods=["GET"])

    def test(self, image_url, uset_background_request):
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        chat_model = ChatOpenAI(model_name="gpt-4o", openai_api_key=OPENAI_API_KEY)
        prompt = self._get_prompt(chat_model, image_url, uset_background_request)

        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.images.generate(
            model="dall-e-3",
            prompt="A futuristic cyberpunk city with neon lights at night",
            size="1024x1024",
        )

        # 생성된 이미지 URL 출력
        image_url = response.data[0].url
        print(f"Generated Image URL: {image_url}")
        
        # image_url = response["data"][0]["url"]
        # print(f"🖼️ 생성된 이미지 URL: {image_url}")
        
        # 이미지 다운로드 및 표시
        image_response = requests.get(image_url)
        img = Image.open(BytesIO(image_response.content))
        img.show()
        
        return image_url
    

    def _get_prompt(self, chat_model, image_url, user_background_request):
        # 이미지를 바이너리 데이터로 로드
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()

        # GPT-4o에게 이미지와 함께 요청
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI assistant that analyzes images and generates photorealistic prompts for DALL·E 3."},
                {"role": "user", "content": [
                    {"type": "text", "text": f"Analyze this image and identify the main object. The user wants to change the background to: '{user_background_request}'. Generate a detailed photorealistic prompt for DALL·E 3 while preserving the main object."},
                    {"type": "image", "image": image_data}
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
