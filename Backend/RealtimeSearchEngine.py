import time
import json
import os

from groq import Groq
from dotenv import dotenv_values
from ddgs import DDGS

# ==========================================
# LOAD ENV
# ==========================================

env = dotenv_values(".env")

USERNAME = env.get("Username", "User")
ASSISTANT_NAME = env.get("Assistantname", "Vani")
API_KEY = env.get("GroqAPIKey")

# ==========================================
# GROQ CLIENT
# ==========================================

client = Groq(
    api_key=API_KEY
)

# ==========================================
# CHAT LOG
# ==========================================

CHATLOG_PATH = "Data/ChatLog.json"

if not os.path.exists("Data"):
    os.makedirs("Data")

if not os.path.exists(CHATLOG_PATH):

    with open(CHATLOG_PATH, "w") as f:
        json.dump([], f)

# ==========================================
# SYSTEM PROMPT
# ==========================================

SYSTEM_PROMPT = f"""
You are {ASSISTANT_NAME}, a fast and intelligent AI assistant.

Rules:
- Reply only in English.
- Reply fast.
- Keep answers short and smart.
- Use professional grammar.
- Avoid unnecessary explanations.
"""

# ==========================================
# SEARCH CACHE
# ==========================================

SEARCH_CACHE = {}

# ==========================================
# SEARCH KEYWORDS
# ==========================================

SEARCH_KEYWORDS = [
    "latest",
    "news",
    "today",
    "weather",
    "price",
    "who is",
    "what is",
    "update",
    "search",
    "internet",
    "current"
]

# ==========================================
# MEMORY
# ==========================================

chat_history = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]

# ==========================================
# FAST INTERNET SEARCH
# ==========================================

def internet_search(query):

    # CACHE
    if query in SEARCH_CACHE:
        return SEARCH_CACHE[query]

    try:

        results_text = ""

        with DDGS() as ddgs:

            results = ddgs.text(
                query,
                max_results=2
            )

            for result in results:

                title = result.get("title", "")
                body = result.get("body", "")

                results_text += f"{title}: {body}\n"

        SEARCH_CACHE[query] = results_text

        return results_text

    except:
        return ""

# ==========================================
# CHECK SEARCH NEEDED
# ==========================================

def needs_search(query):

    query = query.lower()

    return any(
        keyword in query
        for keyword in SEARCH_KEYWORDS
    )

# ==========================================
# SAVE CHAT
# ==========================================

def save_chat():

    try:

        with open(
            CHATLOG_PATH,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                chat_history[-10:],
                f
            )

    except:
        pass

# ==========================================
# MAIN CHATBOT
# ==========================================

def RealtimeSearchEngine(query):

    global chat_history

    try:

        # USER MESSAGE
        chat_history.append({
            "role": "user",
            "content": query
        })

        # SHORT MEMORY
        chat_history = chat_history[-6:]

        # INTERNET DATA
        web_data = ""

        # SEARCH ONLY IF NEEDED
        if needs_search(query):

            web_data = internet_search(query)

        # FINAL MESSAGES
        final_messages = [

            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }

        ]

        # ADD WEB DATA
        if web_data:

            final_messages.append({

                "role": "system",

                "content": f"""
Internet Information:

{web_data}

Use only if relevant.
"""
            })

        # ADD CHAT HISTORY
        final_messages.extend(chat_history)

        # FAST AI RESPONSE
        completion = client.chat.completions.create(

            model="llama-3.1-8b-instant",

            messages=final_messages,

            # SPEED SETTINGS
            temperature=0.3,
            max_tokens=60,
            top_p=1,

            stream=True
        )

        answer = ""

        print(
            f"\n{ASSISTANT_NAME}: ",
            end="",
            flush=True
        )

        # STREAM OUTPUT
        for chunk in completion:

            content = (
                chunk
                .choices[0]
                .delta
                .content
            )

            if content:

                print(
                    content,
                    end="",
                    flush=True
                )

                answer += content

        print("\n")

        # SAVE RESPONSE
        chat_history.append({

            "role": "assistant",
            "content": answer

        })

        save_chat()

        return answer

    except Exception as e:

        print(f"\nError: {e}\n")

        return "Error"

# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    print(f"{ASSISTANT_NAME} is Ready...\n")

    while True:

        query = input("You: ").strip()

        if not query:
            continue

        if query.lower() in [
            "exit",
            "quit",
            "bye"
        ]:
            break

        start = time.time()

        RealtimeSearchEngine(query)

        end = time.time()

        print(
            f"Response Time: "
            f"{round(end - start, 2)} sec\n"
        )













