# ai_core.py
import os
from google import genai
from google.genai.errors import APIError
from typing import Dict, List, Tuple

# ai_core.py
# ... (imports) ...

# --- MODES AND INSTRUCTIONS ---
MODE_INSTRUCTIONS = {
    "Academic Assistant (Default)": "You are a student-centric Academic Assistant (Student GPT). Always respond in clear, grammatically correct English. Explain every question, provide examples, and suggest a next step.",
    "Maths Expert": "You are a Math Specialist. Always respond in clear, grammatically correct English. Solve every question step-by-step using algebraic/arithmetic methods. Always use LaTeX for formulas (e.g., $y=mx+c$). Explain the principle before the final answer. Suggest practice problems.",
    "General Knowledge Guru": "You are a General Knowledge Expert. Always respond in clear, grammatically correct English. Provide concise, factual, and up-to-date answers. Focus on quick facts and lists rather than detailed analysis. Focus on History, Geography, and Science facts.",
    "Creative Writing Coach": "You are a creative writing coach. Always respond in clear, grammatically correct English. Help students with stories, poetry, and essays. Assist with grammar checks and plot ideas. Always maintain a positive and encouraging tone."
}

# ... (rest of the file remains the same) ...
def initialize_gemini_client() -> genai.Client | None:
    """Gemini Client ko API key se initialize karta hai."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # None return karenge, aur frontend error dikhayega
        return None
    
    try:
        client = genai.Client(api_key=api_key)
        return client
    except Exception:
        return None

def get_gemini_response(client: genai.Client, history: List[Tuple[str, str]], user_input: str, mode: str) -> str:
    """
    Gemini API se response fetch karta hai, jahan System Instruction mode ke hisaab se badalti hai.
    """
    if not client:
        return "🚨 Client Not Initialized. Please set a valid GEMINI_API_KEY environment variable."
        
    try:
        system_instruction = MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["Academic Assistant (Default)"])
        
        # History ko API ke format mein prepare karna
        contents = []
        for user_msg, bot_msg in history:
             contents.append({"role": "user", "parts": [{"text": user_msg}]})
             contents.append({"role": "model", "parts": [{"text": bot_msg}]})
        
        contents.append({"role": "user", "parts": [{"text": user_input}]})
        
        # API Call
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config={"system_instruction": system_instruction}
        )
        
        return response.text
    
    except APIError as e:
        error_message = str(e)
        if 'API key not valid' in error_message:
             return f"🚨 API ERROR: Invalid API Key. Please ensure your GEMINI_API_KEY is correct."
        return f"🚨 API Error: Could not connect to Gemini. Error details: {e}"
    
    except Exception as e:
        return f"❌ An unexpected error occurred: {e}"