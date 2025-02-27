from langchain_community.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import os
import replicate
import requests

from src.utils.datetime_helper import CurrentDateTime

class OpenAIModel:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.open_ai_model = ChatOpenAI(model = "gpt-4o", temperature = 0.7, openai_api_key = openai_api_key)
        self.history = ""

    def request(self, image_url, user_request):
        guide_text = self._create_guide_text(image_url, user_request)
        guide_image_url = self._create_guide_image_url(guide_text)
        return guide_text, guide_image_url
    
    def _create_guide_text(self, image_url, user_request):
        message = self._create_message(image_url, user_request)
        response = self.open_ai_model.invoke(message)
        guide_text = response.content
        self.history = guide_text
        return guide_text

    def _create_message(self, image_url, user_request):
        messages = []

        if self._is_request_image_guide(image_url, user_request): # Image와 Text가 모두 있는 경우 : 사진에 의도를 추가하여 가이드 생성
            messages.append(self._create_image_guide(image_url, user_request))
           
        elif self._is_request_image_feedback(image_url, user_request): # Image만 들어온 경우 : 이전 가이드를 기반으로 현재 이미지의 가이드 생성
            messages.append(self._create_image_feedback(image_url, user_request))
            
        elif self._is_request_detail_guide(image_url, user_request): # Text만 들어온 경우 : 이전 사진과 이전 가이드를 기반으로 더 세부적인 가이드 생성
            messages.append(self._create_detail_guide(image_url, user_request))

        else: # 둘 다 안들어온 경우
            # TODO: 에러처리
            pass

        return messages
    
    def _is_request_image_guide(self, image_url, user_request):
        return bool(image_url and user_request)

    def _is_request_image_feedback(self, image_url, user_request):
        return bool(image_url and not user_request)

    def _is_request_detail_guide(self, image_url, user_request):
        return bool(not image_url and user_request)
    
    def _create_image_guide(self, image_url, user_request):
        prompt = f"""
            인물 사진을 분석하고 피드백을 제공합니다. 사용자가 '{user_request}'라고 요청했습니다. 
            우선, 현재 사진이 어떤지, 잘 찍었는지 간단히 판단해주세요.
            구도 조정, 포즈&표정, 카메라 앵글, 광원의 위치, 줌인·줌아웃 등의 관점에서 개선이 필요한 점이 있는 요소에 대해서만 설명해주고, 개선할 필요가 없는 요소는 생략해주세요.
        """
        
        messages = [
            SystemMessage(content="당신은 사진 전문가입니다. 사용자에게 친절한 말투로 알려주세요."),
            HumanMessage(content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}}
            ])
        ]
        return messages

    def _create_image_feedback(self, image_url, user_request):
        prompt = f"""
            사용자가 '{user_request}'라고 추가 요청했습니다. \n
            {self.history}
            사용자의 질문에 대한 답변을 해주세요.
            이전에 받은 피드백과 사용자의 추가 요청을 반영하여, 현재 사진에서 어떻게 수정해야할지 구체적으로 알려주세요.\n
        """
        
        messages = [
            SystemMessage(content="당신은 사진 전문가입니다. 사용자에게 친절한 말투로 알려주세요."),
            HumanMessage(content=prompt)
        ]
        return messages

    def _create_detail_guide(self, image_url, user_request):
        prompt = f"""
            사용자가 새로운 사진을 업로드했습니다.
            기존 피드백: {self.history}
            새로운 사진이 피드백을 잘 반영했다면 칭찬의 글을 남겨주세요. 백점 만점의 몇 점인지 알려주세요.
            추가적으로 수정이 필요한 부분이 있다면 알려주세요.
        """
            
        messages = [
            SystemMessage(content="당신은 사진 전문가입니다. 사용자에게 친절한 말투로 알려주세요."),
            HumanMessage(content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}}
            ])
        ]

        return messages

    def _create_guide_image_url(self, user_request):
        prompt = f"""
            Describe the size of the image and the size of the subject within it.
            Provide a highly detailed description of the subject’s clothing, including the top, bottom, and shoes, specifying color, material, and fit.
            Describe the weather and background in great detail.
            Give a comprehensive description of the entire scene so that even someone who has never seen the photo can fully visualize it.

            Based on {self.history}, describe the best camera angle and composition for the subject, such as head shot, upper body shot, half body shot, full body shot, bird’s eye shot, drone shot, high angle shot, from above, knee shot, etc.
            Specify the exact placement and proportion of the subject within the rule of thirds, providing precise measurements (e.g., lower center of the frame, occupying 1/2 of the image in a smaller composition).

            To satisfy {user_request}, describe in detail the ideal facial expression and pose the subject should take.

            Write a highly detailed description of the entire scene within approximately 1000 characters so that anyone can accurately visualize it.
            """

        input = {
            "prompt": prompt,
            "aspect_ratio": "3:4",
            "prompt_upsampling": True
        }

        output = replicate.run(
            "black-forest-labs/flux-1.1-pro",
            input = input
        )

        image_file_path = f"./result_histories/{CurrentDateTime()}.jpg"
        with open(image_file_path, "wb") as file:
            file.write(output.read())

        imgbb_api_key = os.getenv("IMGBB_API_KEY")
        IMAGE_PATH = image_file_path
        # 🔹 API 요청 URL
        UPLOAD_URL = "https://api.imgbb.com/1/upload"

        # 🔹 이미지 업로드 요청
        with open(IMAGE_PATH, "rb") as file:
            response = requests.post(UPLOAD_URL, data={"key": imgbb_api_key}, files={"image": file})

        # 🔹 응답 결과 확인
        if response.status_code == 200:
            result = response.json()
            image_url = result["data"]["url"]
            print(f"✅ 이미지 업로드 성공! URL: {image_url}")
        else:
            print(f"❌ 업로드 실패! 오류 코드: {response.status_code}, 메시지: {response.text}")

        return image_url
