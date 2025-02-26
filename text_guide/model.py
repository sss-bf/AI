import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# .env 파일 로드
load_dotenv()

# 환경 변수에서 OPENAI API 키 가져오기
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("환경 변수 OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

# GPT-4o 모델 초기화
llm = ChatOpenAI(model="gpt-4o", temperature=0.7, openai_api_key=openai_api_key)

# 초기 사진 피드백 생성
def process_photo_feedback(image_url, user_preference):
    """
    사용자의 요청을 반영하여 촬영 피드백을 생성하는 함수.
    """
    prompt = f"""
    사용자의 요청: '{user_preference}'
    제공된 사진을 분석하고 촬영 피드백을 제공하세요.
    구도, 포즈, 조명, 각도, 줌 등에 대한 조언을 포함해주세요.
    """
    
    messages = [
        SystemMessage(content="당신은 사진 전문가입니다."),
        HumanMessage(content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": image_url}}
        ])
    ]

    response = llm(messages)
    return response.content

# 새로운 사진 평가 및 피드백 업데이트
def update_photo_feedback(new_image_url, user_preference, old_feedback):
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

    response = llm(messages)
    return response.content
