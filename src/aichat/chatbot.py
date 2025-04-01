from openai import OpenAI
import os 
from pathlib import Path
from dotenv import load_dotenv

class AiChat():
    def __init__(self):
        #gets path to .env file
        env_path = Path(__file__).resolve().parent.parent / '.env'
        load_dotenv(dotenv_path=env_path)

        self.APIKEY = os.getenv('AI_API_KEY')

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.APIKEY,
        )

    async def get_response(self, query):
        completion = self.client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=[
                {
                    "role": "user",
                    "content": f'{query}. Use max of 1000 characters in response'
                }
            ]
        )

        response = completion.choices[0].message.content

        return response