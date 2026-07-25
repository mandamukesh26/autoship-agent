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
        
        # Backup: OpenRouter with multiple reliable free models
        self.backup_client = OpenAI(
            base_url=os.getenv("OPENROUTER_BASE_URL"),
            api_key=os.getenv("OPENROUTER_API_KEY")
        )
        self.backup_models = [
            "meta-llama/llama-3.3-70b-instruct:free",
            "google/gemini-2.0-flash-exp:free",
            "qwen/qwen-2.5-72b-instruct:free"
        ]
    
    def ask(self, messages, response_format=None):
        """Try primary first, fallback to backup if fails"""
        
        # Try Groq first (FAST)
        try:
            print("🚀 Using Primary (Groq)...")
            response = self.primary_client.chat.completions.create(
                model=self.primary_model,
                messages=messages,
                response_format=response_format or {"type": "text"},
                temperature=0.3,
                max_tokens=4000
            )
            content = response.choices[0].message.content
            if content and len(content.strip()) > 0:
                return content
            raise Exception("Empty response from primary")
            
        except Exception as e:
            print(f"⚠️  Primary failed: {str(e)[:100]}")
            print("🔄 Trying backup models...")
            
            last_error = None
            for model in self.backup_models:
                try:
                    print(f"   → Trying {model}...")
                    response = self.backup_client.chat.completions.create(
                        model=model,
                        messages=messages,
                        response_format=response_format or {"type": "text"},
                        temperature=0.3,
                        max_tokens=4000,
                        extra_headers={
                            "HTTP-Referer": "https://autoship-agent.onrender.com",
                            "X-Title": "AutoShip Agent"
                        }
                    )
                    content = response.choices[0].message.content
                    if content and len(content.strip()) > 0:
                        print(f"   ✅ Success with {model}")
                        return content
                except Exception as backup_error:
                    last_error = backup_error
                    print(f"   ❌ Failed: {str(backup_error)[:80]}")
                    continue
            
            raise Exception(f"All APIs failed. Last error: {last_error}")

# Global instance
ai = AIClient()
