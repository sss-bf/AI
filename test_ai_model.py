import openai
import requests
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import os

class AIModel:
    def __init__(self):
        load_dotenv()
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key = openai_api_key)
        self.gpt_model = "gpt-4o"
        self.dalle_model = "dall-e-3"
    
    def test_request(self, prompt):
        gpt_response = self.client.chat.completions.create(
            model = self.gpt_model,
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt}
                    ],
                }
            ],
            max_tokens = 500
        )
        guide_text = gpt_response.choices[0].message.content
        return guide_text

    def request(self, prompt, image_url):
        # Read file from URL
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))

        # Request openai API (GPT Model)
        gpt_response = self.client.chat.completions.create(
            model = self.gpt_model,
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            max_tokens = 500
        )
        guide_text = gpt_response.choices[0].message.content
        
        # Request openai API (DALLE Model)
        dalle_prompt = f"Create an image based on this description: {guide_text}"
        result_image_size = "1024x1024"
        dalle_response = self.client.images.generate(
            model = self.dalle_model,
            prompt = dalle_prompt,
            n = 1,
            size = result_image_size
        )
        guide_image_url = dalle_response.data[0].url

        # NOTE: (for Test) Save the created new image.
        response = requests.get(guide_image_url)
        image = Image.open(BytesIO(response.content))
        image.save("NewImage.jpg", "JPEG")

        return guide_text, guide_image_url

# NOTE: (for Test)
if __name__ == "__main__":
    model = AIModel()
    # guide_text, guide_image_url = model.request("이 사진에 대해 설명해줘", "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png")
    # print(guide_text, guide_image_url)
    guide_text = model.test_request("안녕하세요")
    print(guide_text)
