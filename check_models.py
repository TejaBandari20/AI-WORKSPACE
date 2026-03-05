from google import genai
import os

# 1. Setup
api_key = input("Enter your Gemini API Key: ").strip()
client = genai.Client(api_key=api_key)

# 2. List Models
print("\nChecking available models...")
try:
    # We list all models and filter for ones that support 'generateContent'
    models = client.models.list()
    
    print("\n✅ AVAILABLE MODELS:")
    found_any = False
    for m in models:
        # We check if the model supports content generation (chat)
        if "generateContent" in m.supported_actions:
            # Print the clean name (e.g., 'gemini-1.5-flash-001')
            print(f" - {m.name.split('/')[-1]}")
            found_any = True
            
    if not found_any:
        print("No content generation models found. Check your API key permissions.")

except Exception as e:
    print(f"Error listing models: {e}")

input("\nPress Enter to exit...")