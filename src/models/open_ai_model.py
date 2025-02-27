from langchain_community.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import os

class OpenAIModel():
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.open_ai_model = ChatOpenAI(model = "gpt-4o", temperature = 0.7, openai_api_key = openai_api_key)
        self.history = ""

    # 1. 초기 사진 피드백 생성
    def process_photo_feedback(self, image_url, user_preference):
        """
        사용자의 요청을 반영하여 촬영 피드백을 생성하는 함수.
        """
        prompt = f"""
            인물 사진을 분석하고 피드백을 제공합니다. 사용자가 '{user_preference}'라고 요청했습니다. \n
            우선, 현재 사진이 어떤지, 잘 찍었는지 판단해주세요.\n
            구도 조정, 포즈&표정, 카메라 앵글, 광원의 위치, 줌인·줌아웃 관점에서 개선이 필요한 점이 있는 요소에 대해서만 설명해주고, 개선할 필요가 없는 요소는 생략해주세요.
        """
        
        messages = [
            SystemMessage(content="당신은 사진 전문가입니다."),
            HumanMessage(content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}}
            ])
        ]
        
        response = self.open_ai_model(messages)
        return response.content
    
    # 2. 추가 질문 처리
    def answer_feedback_questions(self, feedback, user_question):
        """
        사용자가 피드백에 대해 추가 질문을 할 경우 응답을 생성하는 함수.
        """
        prompt = f"""
            사용자가 '{user_question}'라고 추가 요청했습니다. \n
            {feedback}
            이전에 받은 피드백과 사용자의 추가 요청을 반영하여, 현재 사진에서 어떻게 수정해야할지 구체적으로 알려주세요.\n
        """
        
        messages = [
            SystemMessage(content="당신은 사진 전문가입니다."),
            HumanMessage(content=prompt)
        ]
        
        response = self.open_ai_model(messages)
        return response.content

    # 3. 새로운 사진 평가 및 피드백 업데이트
    def update_photo_feedback(self, new_image_url, user_preference, old_feedback):
        """
        새로운 사진을 평가하여 기존 피드백을 반영한 추가 피드백을 생성.
        """
        prompt = f"""
        사용자가 새로운 사진을 업로드했습니다.
        기존 피드백: {old_feedback}
        새로운 사진이 피드백을 얼마나 반영했는지 평가하고, 추가 조언을 제공하세요.
        """
        
        messages = [
            SystemMessage(content="당신은 사진 전문가입니다."),
            HumanMessage(content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": new_image_url}}
            ])
        ]
        
        response = self.open_ai_model(messages)
        return response.content
    
    def request(self, image_url, user_request):
        prompt = ""
        messages = [SystemMessage(content="당신은 사진 전문가입니다.")]

        # TODO: 기존 피드백 내용이 없는 경우에는 빈칸으로 들어간다. 이것에 대한 프롬프트 엔지니어링을 추가로 해줘야 할까?
        if image_url is None or image_url == "":
            prompt = f"""
                사용자가 '{user_request}'라고 추가 요청했습니다. \n
                기존 피드백: [{self.history}]
                이전에 받은 피드백과 사용자의 추가 요청을 반영하여, 현재 사진에서 어떻게 수정해야할지 구체적으로 알려주세요.\n
                """
            messages.append(HumanMessage(content=prompt))
        elif user_request is None or user_request == "":
            prompt = f"""
                사용자가 새로운 사진을 업로드했습니다.
                기존 피드백: [{self.history}]
                새로운 사진이 피드백을 얼마나 반영했는지 평가하고, 추가 조언을 제공하세요.
                """
            messages.append(HumanMessage(content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]))
        else:
            prompt = f"""
                인물 사진을 분석하고 피드백을 제공합니다. 사용자가 '{user_request}'라고 요청했습니다. \n
                우선, 현재 사진이 어떤지, 잘 찍었는지 판단해주세요.\n
                구도 조정, 포즈&표정, 카메라 앵글, 광원의 위치, 줌인·줌아웃 관점에서 개선이 필요한 점이 있는 요소에 대해서만 설명해주고, 개선할 필요가 없는 요소는 생략해주세요.
                """
            messages.append(HumanMessage(content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]))

        response = self.open_ai_model.invoke(messages)
        guide_text = response.content
        self.history = guide_text

        return guide_text
