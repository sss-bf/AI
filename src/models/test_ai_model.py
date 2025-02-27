import openai
import os
from src.utils.image_file_helper import ImageFileHelper

class TestAIModel:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key = openai_api_key)
        self.gpt_model = "gpt-4o"
        self.dalle_model = "dall-e-3"

    def request(self, prompt, image_url):
        image_file_helper = ImageFileHelper()
        image = image_file_helper.get_url_from_image(image_url)

        guide_text = self._get_gpt_response(prompt, image_url)
        guide_image_url = self._get_dalle_response(guide_text)

        # NOTE: (for Test) Save the created new image.
        image_file_helper.save_image_from_url(guide_image_url)
        
        return guide_text, guide_image_url
    
    def _get_gpt_response(self, prompt, image_url):
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
        return guide_text

    def _get_dalle_response(self, guide_text):
        dalle_prompt = f"Create an image based on this description: {guide_text}"
        result_image_size = "1024x1024"
        dalle_response = self.client.images.generate(
            model = self.dalle_model,
            prompt = dalle_prompt,
            n = 1,
            size = result_image_size
        )
        guide_image_url = dalle_response.data[0].url
        return guide_image_url
