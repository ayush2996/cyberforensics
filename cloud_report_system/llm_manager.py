from groq import Groq
from config import settings

class LLMManager:
    def __init__(self):
        self.groq = Groq(api_key=settings.GROQ_API_KEY)
    
    def generate(self, prompt, system_prompt=None, max_tokens=1024):
        """Generate text using Groq API"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        return response.choices[0].message.content

llm = LLMManager()
