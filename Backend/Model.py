import os
from groq import Groq
from rich import print
from dotenv import dotenv_values

# Load Environment Variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Client setup
client = Groq(api_key=GroqAPIKey)

funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder"
]

# Preamble को और सख्त (Strict) बनाया गया है ताकि मॉडल फालतू बात न करे
preamble = """
You are a Decision-Making Model. 
Classify the user query into one or more of these functions: {funcs}.
Output format: 'function_name (parameter)'
Strict Rules:
1. ONLY output the classification, no explanations.
2. If multiple tasks, separate by comma.
3. Examples:
   - 'open notepad' -> 'open (notepad)'
   - 'how is the weather' -> 'realtime (weather)'
   - 'hello' -> 'general (hello)'
""".format(funcs=", ".join(funcs))

def FirstLayerDMM(prompt: str):
    try:
        # ChatHistory के बजाय सीधे Prompt भेजें (Decision Making के लिए History की ज़रूरत कम होती है, इससे स्पीड बढ़ेगी)
        messages = [
            {"role": "system", "content": preamble},
            {"role": "user", "content": prompt}
        ]

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=messages,
            temperature=0.1, # कम तापमान = ज्यादा सटीक जवाब
            max_tokens=50,   # कम टोकन = ज्यादा स्पीड
        )

        response = completion.choices[0].message.content.strip().lower()
        
        # क्लीनिंग लॉजिक: फालतू लाइन्स हटाना
        tasks = [t.strip() for t in response.split(",") if t.strip()]

        final_tasks = []
        for task in tasks:
            for func in funcs:
                if task.startswith(func):
                    final_tasks.append(task)
        
        # अगर मॉडल कुछ न पहचान पाए तो डिफ़ॉल्ट 'general' कर दें
        return final_tasks if final_tasks else [f"general ({prompt})"]

    except Exception as e:
        return [f"error ({e})"]

if __name__ == "__main__":
    print("[bold green]Decision Model Active (Llama 3.1)...[/bold green]")
    while True:
        try:
            user_query = input(">>> ").strip()
            if not user_query: continue
            
            result = FirstLayerDMM(user_query)
            print(f"[bold yellow]Result:[/bold yellow] {result}")
            
        except KeyboardInterrupt:
            break

