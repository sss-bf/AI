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

# 1. 초기 사진 피드백 생성
def process_photo_feedback(image_url, user_preference):
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
    
    response = llm(messages)
    return response.content

# 2. 추가 질문 처리
def answer_feedback_questions(feedback, user_question):
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
    
    response = llm(messages)
    return response.content

# 3. 새로운 사진 평가 및 피드백 업데이트
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

# 4. 인퍼런스 실행 로직
def run_photo_feedback_system():
    """
    사용자의 입력을 받아서 사진 피드백을 제공하고, 피드백에 대해 추가 질문을 받고, 새로운 사진을 평가하는 흐름을 실행.
    """
    print("사진 피드백 시스템을 시작합니다.\n")
    image_url = input("사진의 URL을 입력하세요: ")
    user_preference = input("어떤 점을 개선하고 싶은지 입력하세요: ")
    
    feedback = process_photo_feedback(image_url, user_preference)
    print("\n초기 피드백:\n", feedback)
    
    while True:
        action = input("\n추가 질문(Q) | 새로운 사진 평가(N) | 종료(E): ").strip().lower()
        
        if action == "q":
            user_question = input("질문을 입력하세요: ")
            answer = answer_feedback_questions(feedback, user_question)
            print("\n질문에 대한 답변:\n", answer)
        
        elif action == "n":
            new_image_url = input("새로운 사진의 URL을 입력하세요: ")
            feedback = update_photo_feedback(new_image_url, user_preference, feedback)
            print("\n새로운 피드백:\n", feedback)
        
        elif action == "e":
            print("시스템을 종료합니다.")
            break
        
        else:
            print("올바른 입력을 해주세요 (Q, N, E).")

if __name__ == "__main__":
    run_photo_feedback_system()
