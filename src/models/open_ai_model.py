# from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import os
import replicate
import requests

from src.utils.datetime_helper import CurrentDateTime
from src.utils.image_file_helper import ImageFileHelper
import json

class OpenAIModel:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.open_ai_model = ChatOpenAI(model = "gpt-4o", temperature = 0.7, openai_api_key = openai_api_key)
        self.history = ""
        self.last_image_url = ""
        self.url = "https://api.developer.pixelcut.ai/v1/generate-background"

    def request_guide(self, image_url, user_request):
        # 이미지 전처리 (리사이즈)
        image_url = self._preprocess_image(image_url)

        guide_text = self._create_guide_text(image_url, user_request)

        image_prompt = guide_text
        if self._is_request_detail_guide(image_url, user_request):
            image_prompt = self._create_image_prompt(self.last_image_url, user_request)
        elif self._is_request_image_guide(image_url, user_request):
            self.last_image_url = ""
            image_prompt = self._create_image_prompt(image_url, user_request)
        else:
            image_prompt = self._create_image_prompt(image_url, user_request)

        guide_image_url = self._create_guide_image_url(image_prompt)
        self.last_image_url = guide_image_url
        return guide_text, guide_image_url
    
    def _preprocess_image(self, image_url):
        imageFileHelper = ImageFileHelper()
        image_file_path = imageFileHelper.save_image_from_url(image_url)
        print(image_file_path)
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
    
    def _create_guide_text(self, image_url, user_request):
        message = self._create_message(image_url, user_request)
        response = self.open_ai_model.invoke(message)
        guide_text = response.content
        if self._is_request_image_guide(image_url, user_request):
            self.history = ""
        else:
            self.history = guide_text
        return guide_text

    def _create_message(self, image_url, user_request):
        messages = []

        if self._is_request_image_guide(image_url, user_request): # Image와 Text가 모두 있는 경우 : 사진에 의도를 추가하여 가이드 생성
            print("Both", bool(image_url), bool(user_request))
            messages = self._create_image_guide(image_url, user_request)
           
        elif self._is_request_image_feedback(image_url, user_request): # Image만 들어온 경우 : 이전 가이드를 기반으로 현재 이미지의 가이드 생성
            print("Image Only", bool(image_url), bool(user_request))
            messages = self._create_image_feedback(image_url, user_request)
            
        elif self._is_request_detail_guide(image_url, user_request): # Text만 들어온 경우 : 이전 사진과 이전 가이드를 기반으로 더 세부적인 가이드 생성
            print("Text Only", bool(image_url), bool(user_request))
            messages = self._create_detail_guide(image_url, user_request)

        else: # 둘 다 안들어온 경우
            raise Exception("Critical Error!!!!! 발생하면 안되는 일이 발생했다!!!!")

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

    def _create_detail_guide(self, image_url, user_request):
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
    
    def _create_image_prompt(self, image_url, user_request):
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
        
        messages = [
            SystemMessage(content="You are someone who describes photographs. Describe the image so vividly and precisely that even someone who has not seen it can perfectly visualize it in their mind."),
            HumanMessage(content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}}
            ])
        ]

        response = self.open_ai_model.invoke(messages)
        image_prompt = response.content
        self.history = image_prompt
        return image_prompt

    def _create_guide_image_url(self,  prompt):
        input = {
            "prompt": f'{prompt}\n 위 내용을 기반으로 3:4 비율의 이미지를 생성해줘.',
            "aspect_ratio": "3:4",
            "prompt_upsampling": True,
            "width": 270,
            "height": 360
        }

        output = replicate.run(
            "black-forest-labs/flux-1.1-pro",
            input = input
        )

        directory = "./result_histories"
        if not os.path.isdir(directory):
            os.makedirs(directory)

        image_file_path = f"{directory}/{CurrentDateTime()}.jpg"
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

    def request_retouching(self, image_url, user_request):
        image_url = self._preprocess_image(image_url)
        
        instruction_text = self._create_product_instruction(image_url, user_request)
        
        background_image_prompt = self._create_background_prompt(image_url, user_request)
        background_image_url = self._create_image_background_url(image_url, background_image_prompt)
        return instruction_text, background_image_url

    # 상품 소개글 생성
    def _create_product_instruction(self, image_url, user_request):
        prompt = f"""
            Your task is to:

            1. Analyze the input image of the product
            2. Consider the product information provided by {user_request}
            3. Understand the user's intention in {user_request}
            4. Create compelling, concise product copy that:
                - Highlights the product's key features and benefits
                - Appeals to the emotional needs of potential buyers
                - Uses engaging, persuasive language
                - Is appropriate for social media or secondhand marketplace listings
                - Creates urgency and desire

            Your copy should be brief yet impactful (50-100 words), include emotive language, and emphasize what makes this product special in korean. Format with attention-grabbing headlines and use short paragraphs or bullet points for readability. Focus on creating text that will make someone stop scrolling and want to buy immediately.
            """

        messages = [
            SystemMessage(content="You are a product copywriting specialist for social media and secondhand marketplaces."),
            HumanMessage(content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}}
            ])
        ]

        response = self.open_ai_model.invoke(messages)
        instruction_prompt = response.content
        self.history = instruction_prompt
        return instruction_prompt

    # 배경 이미지 교체를 위한 배경 프롬프트 생성
    def _create_background_prompt(self, image_url, user_request):
        prompt = f"""
            Your task is to:

            1. Analyze the input image containing a product
            2. Understand {user_request}
            3. Return ONLY ONE highly descriptive background prompt that:
            - Complements the product's aesthetics (color, style, shape)
            - Aligns with the user's stated purpose
            - Creates a contextually appropriate setting
            - Uses vivid, specific language with appropriate adjectives
            - Maintains professional product photography standards

            Your response should be ONLY the background prompt itself - no explanations, no options, no additional text. Keep the prompt under 50 words and focus on creating a photorealistic, attractive environment that will enhance the product's appeal.
            """
        
        messages = [
            SystemMessage(content="You are a specialized prompt creator for product photography backgrounds."),
            HumanMessage(content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}}
            ])
        ]

        response = self.open_ai_model.invoke(messages)
        background_prompt = response.content
        self.history = background_prompt
        return background_prompt

    # 사용자의도와 배경 프롬프트를 입력받아 배경 교체된 이미지(url) 생성
    def _create_image_background_url(self, image_url, background_prompt):
        payload = json.dumps({
            "image_url": image_url,
            "image_transform": {
                "scale": 1,
                "x_center": 0.5,
                "y_center": 0.5
            },
            "prompt": background_prompt,
            "negative_prompt": ""
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-API-KEY': 'sk_bb463e61da7043139c11db8365cb3521' # pixiecut api
        }

        response = requests.request("POST", self.url, headers=headers, data=payload)
        data = json.loads(response.content)
        result_url = data["result_url"]

        directory = "./result_histories"
        if not os.path.isdir(directory):
            os.makedirs(directory)

        imageFileHelper = ImageFileHelper()
        image_file_path = imageFileHelper.save_image_from_url(result_url)
        print(image_file_path)
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
