import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class AIClient:
    def __init__(self):
        # Primary: Groq
        self.primary_client = OpenAI(
            base_url=os.getenv("GROQ_BASE_URL"),
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.primary_model = "llama-3.3-70b-versatile"
        
        # Backup: OpenRouter
        self.backup_client = OpenAI(
            base_url=os.getenv("OPENROUTER_BASE_URL"),
            api_key=os.getenv("OPENROUTER_API_KEY")
        )
        self.backup_model = "deepseek/deepseek-chat-v3.1:free"
    
    def ask(self, messages, response_format=None):
        """Try primary first, fallback to backup if fails"""
        
        # Try Groq first (FAST)
        try:
            print("🚀 Using Primary (Groq)...")
            response = self.primary_client.chat.completions.create(
                model=self.primary_model,
                messages=messages,
                response_format=response_format or {"type": "text"},
                temperature=0.3
            )
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"⚠️  Primary failed: {e}")
            print("🔄 Falling back to OpenRouter...")
            
            # Fallback to OpenRouter
            try:
                response = self.backup_client.chat.completions.create(
                    model=self.backup_model,
                    messages=messages,
                    response_format=response_format or {"type": "text"},
                    temperature=0.3,
                    extra_headers={
                        "HTTP-Referer": "http://localhost:8000",
                        "X-Title": "AutoShip Agent"
                    }
                )
                return response.choices[0].message.content
                
            except Exception as e2:
                raise Exception(f"Both APIs failed. Primary: {e}, Backup: {e2}")

# Global instance
ai = AIClient()
