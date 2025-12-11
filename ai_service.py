import google.generativeai as genai
import os
from dotenv import load_dotenv

class AIService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.model = None
        self.configure()

    def configure(self):
        try:
            if self.api_key:
                genai.configure(api_key=self.api_key)
                # Use a more stable model name
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                return True
            return False
        except Exception as e:
            print(f"Error configuring Gemini: {e}")
            return False

    def generate_response(self, prompt, image=None):
        if not self.model:
            return "⚠️ API Key missing or configuration failed."

        try:
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            
            content_input = [prompt]
            if image:
                content_input.append(image)
            
            response = self.model.generate_content(content_input, safety_settings=safety_settings)
            
            if response.candidates and len(response.candidates) > 0:
                if response.candidates[0].content.parts:
                    return response.candidates[0].content.parts[0].text
            
            if response.text:
                return response.text
                
            return "⚠️ No answer generated (empty response)"

        except Exception as e:
            return f"AI Error: {str(e)[:100]}"
