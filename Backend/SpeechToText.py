
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager

from dotenv import dotenv_values
from deep_translator import GoogleTranslator

import os
import time

# ==========================================
# LOAD ENV
# ==========================================

env_vars = dotenv_values(".env")

InputLanguage = env_vars.get(
    "InputLanguage",
    "en-US"
)

# ==========================================
# HTML FOR SPEECH RECOGNITION
# ==========================================

HTML_CODE = f"""
<!DOCTYPE html>
<html>
<body>

<p id="status">Listening...</p>
<p id="output"></p>

<script>

const output = document.getElementById("output");

const recognition =
    new (
        window.SpeechRecognition ||
        window.webkitSpeechRecognition
    )();

recognition.lang = "{InputLanguage}";

recognition.continuous = false;

recognition.interimResults = false;

recognition.maxAlternatives = 1;

recognition.onresult = (event) => {{

    const text =
        event.results[0][0].transcript;

    output.innerText = text;
}};

recognition.onerror = (event) => {{

    console.log(event.error);
}};

recognition.onend = () => {{

    recognition.start();
}};

recognition.start();

</script>

</body>
</html>
"""

# ==========================================
# CREATE DATA FOLDER
# ==========================================

os.makedirs("Data", exist_ok=True)

HTML_FILE = "Data/Voice.html"

with open(
    HTML_FILE,
    "w",
    encoding="utf-8"
) as f:

    f.write(HTML_CODE)

# ==========================================
# CHROME OPTIONS
# ==========================================

chrome_options = Options()

chrome_options.add_argument(
    "--use-fake-ui-for-media-stream"
)

chrome_options.add_argument(
    "--headless=new"
)

chrome_options.add_argument(
    "--log-level=3"
)

chrome_options.add_argument(
    "--disable-extensions"
)

chrome_options.add_argument(
    "--disable-gpu"
)

chrome_options.add_argument(
    "--disable-popup-blocking"
)

# ==========================================
# DRIVER SETUP
# ==========================================

driver = webdriver.Chrome(

    service=Service(
        ChromeDriverManager().install()
    ),

    options=chrome_options
)

# ==========================================
# OPEN HTML
# ==========================================

LINK = (
    "file:///" +
    os.path.abspath(HTML_FILE)
    .replace("\\", "/")
)

driver.get(LINK)

# ==========================================
# TRANSLATOR
# ==========================================

def UniversalTranslator(text):

    try:

        return GoogleTranslator(
            source="auto",
            target="en"
        ).translate(text)

    except:

        return text

# ==========================================
# QUERY MODIFIER
# ==========================================

def QueryModifier(query):

    query = query.strip()

    if not query:
        return ""

    query = query.capitalize()

    question_words = [

        "what",
        "who",
        "where",
        "when",
        "why",
        "how",
        "can",
        "is",
        "are",
        "do"

    ]

    if any(
        query.lower().startswith(word)
        for word in question_words
    ):

        if not query.endswith("?"):

            query += "?"

    else:

        if not query.endswith("."):

            query += "."

    return query

# ==========================================
# MAIN SPEECH FUNCTION
# ==========================================

def SpeechRecognition():

    print("Listening...")

    last_text = ""

    while True:

        try:

            text = driver.find_element(
                By.ID,
                "output"
            ).text.strip()

            # NEW TEXT ONLY
            if text and text != last_text:

                last_text = text

                # CLEAR OUTPUT
                driver.execute_script(
                    """
                    document.getElementById(
                    'output'
                    ).innerText = '';
                    """
                )

                print(
                    f"Recognized: {text}"
                )

                # TRANSLATE
                if "en" not in InputLanguage.lower():

                    text = UniversalTranslator(text)

                return QueryModifier(text)

            time.sleep(0.1)

        except Exception as e:

            print(f"Error: {e}")

            time.sleep(1)

# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    try:

        while True:

            result = SpeechRecognition()

            if result:

                print(
                    f"Final Query: {result}"
                )

    except KeyboardInterrupt:

        driver.quit()