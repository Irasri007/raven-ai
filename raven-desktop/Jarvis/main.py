import pyttsx3
import speech_recognition as sr
import random
import webbrowser
import datetime
import threading
from plyer import notification
import pyautogui
import wikipedia
import pywhatkit as pwk
import user_config
import requests
import os
import urllib.parse
import pickle
import langdetect          

from database import get_connection, init_db   
from auth import register_user, login_user
from chat_logger import log_chat, get_user_chats        # pip install langdetect

init_db() 

GEMINI_API_KEY = "AIzaSyB3Ix8IoychS04ZbGa9Za1IHXbYsoJz7Cc"   # ← Replace with your key
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
)

# =============================================
# 🔔 WAKE WORDS
# =============================================
# Any of these phrases will wake Raven up.
# Google speech is never 100% exact so we include
# common mis-hearings of "hey raven" as well.
WAKE_WORDS = [
    "hey raven",
    "raven",
    "hey raven are you there",
    "are you there",
    "wake up raven",
    "hello raven",
    "hi raven",
    "okay raven",
    "ok raven",
]

# How many seconds of silence before Raven goes
# back to sleep after completing a command.
SLEEP_AFTER_SECONDS = 10


# =============================================
# 🌐 LANGUAGE DETECTION
# =============================================
def detect_language(text: str) -> str:
    """Returns 'hi' for Hindi, 'en' for English (default)."""
    try:
        lang = langdetect.detect(text)
        return lang if lang in ("hi", "en") else "en"
    except Exception:
        return "en"


def raven_respond(command):
    """Your existing Raven logic goes here."""
    return f"Executing: {command}"  # Replace with real Raven response

def start_raven():
    print("=== RAVEN LOGIN ===")
    choice = input("1. Login\n2. Register\nChoose: ")

    if choice == "2":
        username = input("Username: ")
        email = input("Email: ")
        password = input("Password: ")
        register_user(username, email, password)

    # Login
    username = input("Username: ")
    password = input("Password: ")
    user = login_user(username, password)

    if not user:
        print("Access denied.")
        return

    print(f"\n🤖 Raven ready. Hello, {user['username']}!")
    print("Type 'history' to see your past commands, or 'exit' to quit.\n")

    # Main command loop
    while True:
        command = input("You: ").strip()

        if command.lower() == "exit":
            print("Goodbye!")
            break
        elif command.lower() == "history":
            chats = get_user_chats(user["id"])
            for chat in chats:
                print(f"[{chat['timestamp']}] You: {chat['command']}")
                print(f"              Raven: {chat['response']}\n")
        else:
            response = raven_respond(command)
            print(f"Raven: {response}")
            log_chat(user["id"], command, response)  # ✅ Save to DB

if __name__ == "__main__":
    start_raven()
    
def speak(audio: str, lang: str = "en"):
    def run():
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        chosen_voice = voices[0].id
        if lang == "hi":
            for v in voices:
                name_lower = v.name.lower()
                if "hindi" in name_lower or "hemant" in name_lower or "kalpana" in name_lower:
                    chosen_voice = v.id
                    break
        engine.setProperty('voice', chosen_voice)
        engine.setProperty("rate", 165)
        engine.say(audio)
        engine.runAndWait()
        engine.stop()

    t = threading.Thread(target=run)
    t.start()
    t.join()


# =============================================
# 🧠 INTENT MODEL LOAD
# =============================================
try:
    with open("intent_model.pkl", "rb") as f:
        intent_model = pickle.load(f)
    print("✅ Intent model loaded.")
except FileNotFoundError:
    intent_model = None
    print("⚠️  intent_model.pkl not found — using keyword fallback only.")


HINDI_KEYWORD_MAP = {
    "greet":            ["हेलो", "नमस्ते", "hello", "hi", "hey"],
    "get_time":         ["टाइम", "समय", "time", "clock", "baj", "kitne baje", "what time"],
    "get_date":         ["तारीख", "date", "din", "aaj", "today"],
    "image_gen":        ["image", "photo", "picture", "तस्वीर", "इमेज", "generate", "bana", "draw", "create"],
    "wikipedia_search": ["wikipedia", "विकिपीडिया", "wiki"],
    "play_music":       ["म्यूजिक", "music", "gaana", "गाना", "song", "play music", "baja"],
    "open_youtube":     ["youtube", "यूट्यूब", "open youtube"],
    "google_search":    ["google", "गूगल", "search", "dhundo", "ढूंढो", "look up"],
    "translate":        ["translate", "translation", "hindi mein", "अनुवाद"],
    "add_task":         ["task add", "new task", "kaam add", "काम जोड़", "add task", "remind me"],
    "show_tasks":       ["tasks dikhao", "show tasks", "kaam dikhao", "काम दिखाओ", "todo", "my tasks"],
    "whatsapp":         ["whatsapp", "message bhejo", "व्हाट्सएप"],
    "send_email":       ["send email", "email", "mail", "ईमेल"],
    "open_app":         ["open", "kholo", "खोलो", "launch"],
    "exit":             ["exit", "band karo", "bye", "alvida", "बंद करो", "अलविदा", "goodbye", "quit", "stop"],
}


def save_command(command, response):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO command_history (command, response) VALUES (%s, %s)",
        (command, response)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_last_commands(limit=5):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT command, response, timestamp FROM command_history ORDER BY timestamp DESC LIMIT %s",
        (limit,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# Example usage
save_command("play music", "Playing your playlist...")
print(get_last_commands())

def keyword_intent(text: str) -> str | None:
    text_lower = text.lower()
    for intent, keywords in HINDI_KEYWORD_MAP.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                return intent
    return None


def predict_intent(text: str) -> str:
    if intent_model is not None:
        try:
            prediction = intent_model.predict([text])[0]
            score = intent_model.decision_function([text]).max()
            if score >= 0.3:
                return prediction
        except Exception as e:
            print(f"⚠️  Intent model error: {e}")
    kw = keyword_intent(text)
    if kw:
        return kw
    return "ask_ai"


# =============================================
# 🎙️ LISTEN FUNCTION (low-level, no loop)
# =============================================
def listen_once(language: str = 'en-US', timeout: int = 5) -> str:
    """
    Listens for ONE utterance and returns the text.
    Returns empty string "" on silence / error — does NOT loop.
    Used by the wake word listener so it doesn't block forever.
    """
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.3)
            audio = r.listen(source, timeout=timeout, phrase_time_limit=6)
        return r.recognize_google(audio, language=language).lower()
    except sr.WaitTimeoutError:
        return ""
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"Speech service error: {e}")
        return ""
    except Exception:
        return ""


# =============================================
# 🎙️ COMMAND FUNCTION (loops until heard)
# =============================================
def command(language: str = 'en-US') -> str:
    content = ""
    while not content.strip():
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎙️  Listening... (English / Hindi both work)")
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source)
        try:
            content = r.recognize_google(audio, language=language)
            print("You said: " + content)
        except sr.UnknownValueError:
            print("Could not understand, please try again...")
        except sr.RequestError as e:
            print(f"Speech service error: {e}")
    return content


# =============================================
# 😴 WAKE WORD LISTENER
# =============================================
def wait_for_wake_word():
    """
    Stays in a tight loop listening passively.
    Returns only when a wake word is detected.
    Prints a dot every few seconds so you know it's alive.
    """
    print("\n😴 Raven is sleeping")
    dot_counter = 0

    while True:
        heard = listen_once(language='en-US', timeout=3)

        if heard:
            print(f"   (heard: '{heard}')")
            # Check if any wake word appears inside what was heard
            for wake in WAKE_WORDS:
                if wake in heard:
                    return   # ← Wake word confirmed, exit the loop
        else:
            # Print a dot every ~3 silent cycles so the terminal
            # shows the program is still running
            dot_counter += 1
            if dot_counter % 3 == 0:
                print("💤 waiting...", end="\r")


# =============================================
# 🤖 GEMINI — language-aware response
# =============================================
def ask_gemini(user_query: str, lang: str = "en") -> str:
    lang_instruction = (
        "Reply ONLY in Hindi (Devanagari script). Keep it short and conversational."
        if lang == "hi"
        else "Reply ONLY in English. Keep it short and conversational."
    )
    try:
        payload = {
            "contents": [{
                "parts": [{
                    "text": (
                        f"You are Raven, a helpful AI assistant. {lang_instruction}\n\n"
                        f"User: {user_query}"
                    )
                }]
            }]
        }
        response = requests.post(GEMINI_URL, json=payload, timeout=15)
        data = response.json()
        if "candidates" not in data:
            error_msg = data.get("error", {}).get("message", "Unknown error")
            print(f"⚠️  Gemini error: {data}")
            return f"Gemini error: {error_msg}"
        return data['candidates'][0]['content']['parts'][0]['text'].strip()
    except requests.exceptions.Timeout:
        return "Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return "No internet connection."
    except Exception as e:
        return f"Error: {str(e)}"


# =============================================
# 🌐 TRANSLATE TO ENGLISH via Gemini
# =============================================
def translate_to_english(text: str) -> str:
    try:
        payload = {
            "contents": [{
                "parts": [{
                    "text": (
                        "Translate the following text to English. "
                        "Output ONLY the English translation — no explanation, no quotes.\n\n"
                        f"{text}"
                    )
                }]
            }]
        }
        response = requests.post(GEMINI_URL, json=payload, timeout=10)
        data = response.json()
        if "candidates" not in data:
            return text
        result = data['candidates'][0]['content']['parts'][0]['text'].strip()
        print(f"🌐 Translated to English: {result}")
        return result
    except Exception as e:
        print(f"Translation failed: {e}")
        return text


# =============================================
# 🌐 TRANSLATE TO HINDI via Gemini
# =============================================
def translate_to_hindi(text: str) -> str:
    try:
        payload = {
            "contents": [{
                "parts": [{
                    "text": (
                        f"Translate this to Hindi (Devanagari script): {text}\n"
                        "Only give the translation, nothing else."
                    )
                }]
            }]
        }
        response = requests.post(GEMINI_URL, json=payload, timeout=10)
        data = response.json()
        if "candidates" not in data:
            return text
        return data['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception:
        return text


# =============================================
# 🎨 IMAGE GENERATION
# =============================================
def generate_image(prompt: str, lang: str = "en"):
    try:
        detected = detect_language(prompt)
        if detected != "en":
            speak("Translating prompt first..." if lang == "en" else "Pehle translate kar raha hoon...", lang)
            english_prompt = translate_to_english(prompt)
        else:
            english_prompt = prompt

        print(f"📝 Final English prompt: {english_prompt}")

        encoded = urllib.parse.quote(english_prompt)
        image_url = (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width=1024&height=1024&enhance=true&nologo=true"
        )

        print(f"🎨 Image URL: {image_url}")
        speak("Generating image..." if lang == "en" else "Image bana raha hoon...", lang)
        webbrowser.open(image_url)
        speak(
            "Image opened in browser! It may take a few seconds to load." if lang == "en"
            else "Image browser mein khul gayi! Thodi der mein load hogi.",
            lang
        )

    except Exception as e:
        speak("Could not generate image." if lang == "en" else "Image banane mein problem aayi.", lang)
        print(f"Image error: {e}")


# =============================================
# ⚡ HANDLE ONE COMMAND
# =============================================
def handle_command(request: str) -> bool:
    """
    Processes a single spoken command.
    Returns True  → keep listening (stay awake)
    Returns False → go back to sleep
    """
    lang = detect_language(request)
    print(f"🌐 Language: {lang}  |  Input: {request}")

    intent = predict_intent(request)
    print(f"🎯 Intent: {intent}")

    if intent == "greet":
        speak("Hello! How can I help you?" if lang == "en" else "Namaste! Kya kaam hai?", lang)

    elif intent == "get_time":
        now_time = datetime.datetime.now().strftime("%H:%M")
        speak(f"The current time is {now_time}" if lang == "en" else f"Abhi ka samay hai {now_time}", lang)

    elif intent == "get_date":
        now_date = datetime.datetime.now().strftime("%d %B %Y")
        speak(f"Today's date is {now_date}" if lang == "en" else f"Aaj ki tarikh hai {now_date}", lang)

    elif intent == "image_gen":
        speak("What image should I generate?" if lang == "en" else "Kya image chahiye? Batao...", lang)
        img_request = command(language='en-US')
        img_lang = detect_language(img_request)
        generate_image(img_request, lang=img_lang)

    elif intent == "wikipedia_search":
        query = request
        for word in ["wikipedia", "विकिपीडिया", "wiki", "ke baare mein", "batao", "about", "search"]:
            query = query.replace(word, "")
        query = query.strip()
        if not query:
            speak("What should I search?" if lang == "en" else "Kya search karoon?", lang)
        else:
            speak(f"Searching Wikipedia for {query}..." if lang == "en" else f"{query} ke baare mein search kar raha hoon...", lang)
            try:
                result = wikipedia.summary(query, sentences=2)
                print(result)
                speak(result, lang)
            except wikipedia.exceptions.DisambiguationError as e:
                speak(f"Multiple results. Did you mean {e.options[0]}?" if lang == "en" else f"Kai results mile. Kya aap {e.options[0]} ke baare mein pooch rahe hain?", lang)
            except wikipedia.exceptions.PageError:
                speak("Nothing found on Wikipedia." if lang == "en" else "Wikipedia par kuch nahi mila.", lang)
            except Exception as e:
                speak("Search failed." if lang == "en" else "Search mein problem aayi.", lang)
                print(f"Wikipedia error: {e}")

    elif intent == "play_music":
        speak("Playing music!" if lang == "en" else "Gaana chala raha hoon", lang)
        songs = [
            "https://www.youtube.com/watch?v=oafxkMv4xnc",
            "https://www.youtube.com/watch?v=KGx_FZY9cQw",
            "https://www.youtube.com/watch?v=dIVpJEKYNq4",
        ]
        webbrowser.open(random.choice(songs))

    elif intent == "open_youtube":
        speak("Opening YouTube" if lang == "en" else "YouTube khol raha hoon", lang)
        webbrowser.open("https://www.youtube.com")

    elif intent == "google_search":
        query = request
        for word in ["google", "गूगल", "search karo", "search", "dhundo", "ढूंढो", "look up"]:
            query = query.replace(word, "")
        query = query.strip()
        if not query:
            speak("What should I search?" if lang == "en" else "Kya search karoon?", lang)
        else:
            speak(f"Searching for {query}" if lang == "en" else f"Search kar raha hoon: {query}", lang)
            webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(query)}")

    elif intent == "translate":
        speak("What should I translate? Please say it in English.", "en")
        text_to_translate = command(language='en-US')
        translated = translate_to_hindi(text_to_translate)
        print(f"Hindi: {translated}")
        speak(translated, lang="hi")

    elif intent == "add_task":
        task = request
        for word in ["new task", "kaam add", "task add", "काम जोड़", "add task", "remind me"]:
            task = task.replace(word, "")
        task = task.strip()
        if task:
            speak(f"Adding task: {task}" if lang == "en" else f"Task add kar raha hoon: {task}", lang)
            with open("todo.txt", "a", encoding="utf-8") as file:
                file.write(task + "\n")
            speak("Task added!" if lang == "en" else "Task add ho gaya!", lang)
        else:
            speak("What task should I add?" if lang == "en" else "Kaunsa task add karoon?", lang)

    elif intent == "show_tasks":
        try:
            with open("todo.txt", "r", encoding="utf-8") as file:
                tasks = file.read().strip()
            if tasks:
                speak(("Your tasks: " if lang == "en" else "Aaj ka kaam: ") + tasks, lang)
                notification.notify(title="Tasks", message=tasks, timeout=5)
            else:
                speak("Your task list is empty." if lang == "en" else "Todo list khali hai.", lang)
        except FileNotFoundError:
            speak("No tasks yet." if lang == "en" else "Abhi koi task nahi hai.", lang)

    elif intent == "whatsapp":
        speak("Sending WhatsApp message" if lang == "en" else "WhatsApp message bhej raha hoon", lang)
        try:
            pwk.sendwhatmsg("+919569869734", "Hi buddy!", 23, 25, 30)
        except Exception as e:
            speak("WhatsApp failed." if lang == "en" else "WhatsApp message mein problem aayi.", lang)
            print(f"WhatsApp error: {e}")

    elif intent == "send_email":
        speak("Sending email" if lang == "en" else "Email bhej raha hoon", lang)
        try:
            pwk.send_mail(
                "irasrivastava051@gmail.com",
                user_config.gmail_password,
                "Hello", "How are you!",
                "irasrivastava101@gmail.com",
            )
            speak("Email sent!" if lang == "en" else "Email bhej di!", lang)
        except Exception as e:
            speak("Email failed." if lang == "en" else "Email mein problem aayi.", lang)
            print(f"Email error: {e}")

    elif intent == "open_app":
        query = request
        for word in ["open", "kholo", "खोलो", "launch"]:
            query = query.replace(word, "")
        query = query.strip()
        if query:
            speak(f"Opening {query}" if lang == "en" else f"{query} khol raha hoon", lang)
            pyautogui.press("super")
            pyautogui.typewrite(query, interval=0.05)
            pyautogui.sleep(2)
            pyautogui.press("enter")
        else:
            speak("Which app should I open?" if lang == "en" else "Kaunsa app kholoon?", lang)

    elif intent == "exit":
        speak("Goodbye! Going to sleep." if lang == "en" else "Theek hai, alvida!", lang)
        return False   # ← signal: go back to sleep (not full exit)

    else:
        speak("Let me think..." if lang == "en" else "Soch raha hoon...", lang)
        response = ask_gemini(request, lang=lang)
        print(f"\n🤖 Gemini: {response}\n")
        speak(response, lang)

    return True   # ← stay awake for more commands


# =============================================
# 🧠 MAIN PROCESS
# =============================================
def main_process():
    speak("Hello! I am Raven. Say 'Hey Raven' whenever you need me.", lang="en")
    print("✅ Raven started!")
    print("=" * 50)

    while True:                          # ── outer loop: run forever ──
        try:
            # ── SLEEPING: wait for wake word ──────────────────────────
            wait_for_wake_word()

            # ── WOKEN UP ──────────────────────────────────────────────
            speak("Yes, I'm here! How can I help?", lang="en")
            print("\n✅ Raven is AWAKE")

            # ── ACTIVE: keep taking commands until silence or 'bye' ───
            while True:
                print(f"\n🎙️  Waiting for command (will sleep after {SLEEP_AFTER_SECONDS}s silence)...")
                heard = listen_once(language='en-US', timeout=SLEEP_AFTER_SECONDS)

                if not heard:
                    # Silence for SLEEP_AFTER_SECONDS → go back to sleep
                    speak("Going to sleep. Say 'Hey Raven' to wake me up.", lang="en")
                    print("😴 Raven going back to sleep...")
                    break

                # Process the command; if it returns False go back to sleep
                stay_awake = handle_command(heard)
                if not stay_awake:
                    break

        except KeyboardInterrupt:
            speak("Shutting down completely. Goodbye!", lang="en")
            print("\n👋 Raven stopped.")
            break


if __name__ == "__main__":
    main_process()