# app.py — R.A.V.E.N Flask Backend
# Run with: python app.py

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from database import init_db
from auth import register_user, login_user
from chat_logger import log_chat, get_user_chats

import webbrowser
import datetime
import urllib.parse
import random
import pickle

try:
    import wikipedia
    WIKIPEDIA_OK = True
except ImportError:
    WIKIPEDIA_OK = False

try:
    import requests as req_lib
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False

# ── Load intent model ──
try:
    with open("intent_model.pkl", "rb") as f:
        intent_model = pickle.load(f)
    print("✅ Intent model loaded.")
except FileNotFoundError:
    intent_model = None
    print("⚠️  intent_model.pkl not found — using keyword fallback only.")

# ── Gemini config ──
GEMINI_API_KEY = "AIzaSyB3Ix8IoychS04ZbGa9Za1IHXbYsoJz7Cc"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
)

app = Flask(__name__)
CORS(app)
init_db()

# ─────────────────────────────────────────
#  INTENT KEYWORD MAP
# ─────────────────────────────────────────
HINDI_KEYWORD_MAP = {
    "greet":            ["hello", "hi", "hey", "हेलो", "नमस्ते"],
    "get_time":         ["time", "clock", "baj", "kitne baje", "what time", "टाइम", "समय"],
    "get_date":         ["date", "today", "din", "aaj", "तारीख"],
    "image_gen":        ["image", "photo", "picture", "generate", "draw", "create", "तस्वीर", "इमेज", "bana"],
    "wikipedia_search": ["wikipedia", "wiki", "विकिपीडिया"],
    "play_music":       ["music", "song", "play music", "gaana", "baja", "म्यूजिक", "गाना"],
    "open_youtube":     ["youtube", "open youtube", "यूट्यूब"],
    "google_search":    ["google", "search", "dhundo", "look up", "गूगल", "ढूंढो"],
    "translate":        ["translate", "translation", "hindi mein", "अनुवाद"],
    "add_task":         ["add task", "new task", "task add", "remind me", "kaam add", "काम जोड़"],
    "show_tasks":       ["show tasks", "my tasks", "todo", "tasks dikhao", "kaam dikhao", "काम दिखाओ"],
    "exit":             ["exit", "bye", "goodbye", "quit", "stop", "band karo", "alvida", "बंद करो", "अलविदा"],
    "open_app":         ["open", "launch", "kholo", "खोलो"],
}

def keyword_intent(text):
    text_lower = text.lower()
    for intent, keywords in HINDI_KEYWORD_MAP.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                return intent
    return None

def predict_intent(text):
    if intent_model is not None:
        try:
            prediction = intent_model.predict([text])[0]
            score = intent_model.decision_function([text]).max()
            if score >= 0.3:
                return prediction
        except Exception as e:
            print(f"⚠️  Intent model error: {e}")
    kw = keyword_intent(text)
    return kw if kw else "ask_ai"

def ask_gemini(user_query, lang="en"):
    if not REQUESTS_OK:
        return "Gemini unavailable — requests library missing."
    if "YOUR_GEMINI_API_KEY_HERE" in GEMINI_API_KEY:
        return "Please add your Gemini API key in app.py to enable AI responses."
    lang_instruction = (
        "Reply ONLY in Hindi (Devanagari script). Keep it short and conversational."
        if lang == "hi"
        else "Reply ONLY in English. Keep it short and conversational."
    )
    try:
        payload = {"contents": [{"parts": [{"text": f"You are Raven, a helpful AI assistant. {lang_instruction}\n\nUser: {user_query}"}]}]}
        response = req_lib.post(GEMINI_URL, json=payload, timeout=15)
        data = response.json()
        if "candidates" not in data:
            return "Gemini error: " + data.get("error", {}).get("message", "Unknown error")
        return data['candidates'][0]['content']['parts'][0]['text'].strip()
    except req_lib.exceptions.Timeout:
        return "Request timed out. Please try again."
    except req_lib.exceptions.ConnectionError:
        return "No internet connection."
    except Exception as e:
        return f"Error: {str(e)}"

# ─────────────────────────────────────────
#  REAL RAVEN BRAIN
# ─────────────────────────────────────────
def raven_respond(command_text):
    c = command_text.strip()
    c_lower = c.lower()
    intent = predict_intent(c)
    print(f"🎯 Intent: {intent}  |  Input: {c}")

    if intent == "greet":
        return "Hello! how are you iraa "

    elif intent == "get_time":
        now_time = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {now_time}."

    elif intent == "get_date":
        now_date = datetime.datetime.now().strftime("%A, %B %d %Y")
        return f"Today is {now_date}."

    elif intent == "open_youtube":
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube for you! 🎬"

    elif intent == "play_music":
        songs = [
            "https://www.youtube.com/watch?v=oafxkMv4xnc",
            "https://www.youtube.com/watch?v=KGx_FZY9cQw",
            "https://www.youtube.com/watch?v=dIVpJEKYNq4",
        ]
        webbrowser.open(random.choice(songs))
        return "Playing music for you! 🎵"

    elif intent == "google_search":
        query = c_lower
        for word in ["google", "गूगल", "search karo", "search", "dhundo", "ढूंढो", "look up"]:
            query = query.replace(word, "")
        query = query.strip()
        if query:
            webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(query)}")
            return f"Searching Google for: {query} 🔍"
        return "What would you like me to search for?"

    elif intent == "wikipedia_search":
        query = c_lower
        for word in ["wikipedia", "विकिपीडिया", "wiki", "ke baare mein", "batao", "about", "search"]:
            query = query.replace(word, "")
        query = query.strip()
        if not query:
            return "What should I search on Wikipedia?"
        if not WIKIPEDIA_OK:
            webbrowser.open(f"https://en.wikipedia.org/wiki/Special:Search?search={urllib.parse.quote(query)}")
            return f"Opening Wikipedia search for: {query}"
        try:
            result = wikipedia.summary(query, sentences=2)
            return result
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Multiple results found. Did you mean: {e.options[0]}?"
        except wikipedia.exceptions.PageError:
            return "Nothing found on Wikipedia for that query."
        except Exception as e:
            return f"Wikipedia search failed: {str(e)}"

    elif intent == "image_gen":
        subject = c_lower
        for word in ["generate", "create", "draw", "make", "image", "photo", "picture", "of", "a", "an", "the"]:
            subject = subject.replace(word, " ")
        subject = " ".join(subject.split()) or c
        encoded = urllib.parse.quote(subject)
        img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&enhance=true&nologo=true"
        webbrowser.open(img_url)
        return f"Generating image of '{subject}'! Opening in browser 🎨"

    elif intent == "add_task":
        task = c_lower
        for word in ["new task", "kaam add", "task add", "काम जोड़", "add task", "remind me"]:
            task = task.replace(word, "")
        task = task.strip() or c
        try:
            with open("todo.txt", "a", encoding="utf-8") as file:
                file.write(task + "\n")
            return f"Task added: '{task}' ✅"
        except Exception as e:
            return f"Could not save task: {str(e)}"

    elif intent == "show_tasks":
        try:
            with open("todo.txt", "r", encoding="utf-8") as file:
                tasks = file.read().strip()
            if tasks:
                return "Your tasks: " + tasks.replace("\n", " | ") + " 📋"
            return "Your task list is empty!"
        except FileNotFoundError:
            return "No tasks yet. Add one with 'add task [name]'."

    elif intent == "exit":
        return "Goodbye! Raven standing by. 👋"

    elif intent == "open_app":
        query = c_lower
        for word in ["open", "kholo", "खोलो", "launch"]:
            query = query.replace(word, "")
        query = query.strip()
        if query:
            web_apps = {
                "gmail": "https://mail.google.com",
                "maps": "https://maps.google.com",
                "calendar": "https://calendar.google.com",
                "drive": "https://drive.google.com",
                "spotify": "https://open.spotify.com",
                "netflix": "https://www.netflix.com",
                "twitter": "https://www.twitter.com",
                "instagram": "https://www.instagram.com",
                "facebook": "https://www.facebook.com",
                "github": "https://www.github.com",
                "whatsapp": "https://web.whatsapp.com",
            }
            matched_url = next((url for key, url in web_apps.items() if key in query), None)
            if matched_url:
                webbrowser.open(matched_url)
                return f"Opening {query.title()}! 🚀"
            else:
                webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(query)}")
                return f"Searching for {query}..."
        return "Which app should I open?"

    else:
        return ask_gemini(c)


# ─────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    email    = data.get('email', '').strip()
    password = data.get('password', '')
    if not username or not email or not password:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    success = register_user(username, email, password)
    if success:
        return jsonify({'success': True, 'message': 'Account created successfully'})
    return jsonify({'success': False, 'message': 'Username already exists'}), 409


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    if not username or not password:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    user = login_user(username, password)
    if user:
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id':       user['id'],
                'username': user['username'],
                'email':    user['email'],
                'lastLogin': str(user['last_login']) if user['last_login'] else None
            }
        })
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401


@app.route('/api/command', methods=['POST'])
def command():
    data    = request.json
    user_id = data.get('user_id')
    cmd     = data.get('command', '').strip()
    if not user_id or not cmd:
        return jsonify({'success': False, 'message': 'user_id and command are required'}), 400
    response = raven_respond(cmd)
    log_chat(user_id, cmd, response)
    return jsonify({'success': True, 'response': response})


@app.route('/api/history/<int:user_id>', methods=['GET'])
def history(user_id):
    limit = request.args.get('limit', 20, type=int)
    chats = get_user_chats(user_id, limit)
    for c in chats:
        if c.get('timestamp'):
            c['timestamp'] = str(c['timestamp'])
    return jsonify({'success': True, 'history': chats})


# ─────────────────────────────────────────
#  VOICE INPUT — Python speech recognition
#  Called by Electron mic button directly
# ─────────────────────────────────────────
import threading

_listen_thread = None
_listen_result = {'status': 'idle', 'text': ''}

def _do_listen():
    global _listen_result
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        _listen_result = {'status': 'listening', 'text': ''}
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.3)
            audio = r.listen(source, timeout=8, phrase_time_limit=10)
        _listen_result = {'status': 'processing', 'text': ''}
        text = r.recognize_google(audio, language='en-IN')
        _listen_result = {'status': 'done', 'text': text}
    except Exception as e:
        err = str(e)
        if 'timeout' in err.lower() or 'WaitTimeoutError' in err:
            _listen_result = {'status': 'error', 'text': 'No speech detected. Try again.'}
        elif 'UnknownValueError' in err or 'understand' in err.lower():
            _listen_result = {'status': 'error', 'text': 'Could not understand. Speak clearly.'}
        elif 'RequestError' in err:
            _listen_result = {'status': 'error', 'text': 'Speech service error. Check internet.'}
        else:
            _listen_result = {'status': 'error', 'text': f'Mic error: {err[:60]}'}

@app.route('/api/listen/start', methods=['POST'])
def listen_start():
    global _listen_thread, _listen_result
    if _listen_thread and _listen_thread.is_alive():
        return jsonify({'success': False, 'message': 'Already listening'})
    _listen_result = {'status': 'starting', 'text': ''}
    _listen_thread = threading.Thread(target=_do_listen, daemon=True)
    _listen_thread.start()
    return jsonify({'success': True, 'message': 'Listening started'})

@app.route('/api/listen/status', methods=['GET'])
def listen_status():
    return jsonify({'success': True, **_listen_result})

@app.route('/api/listen/stop', methods=['POST'])
def listen_stop():
    global _listen_result
    _listen_result = {'status': 'idle', 'text': ''}
    return jsonify({'success': True})


# ─────────────────────────────────────────
#  SERVE FRONTEND — Flask hosts index.html
# ─────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def serve_index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(BASE_DIR, filename)


if __name__ == '__main__':
    print("=" * 50)
    print("  R.A.V.E.N is starting...")
    print("  Open this in Chrome: http://localhost:5000")
    print("  (Stop any other server running on 5501 etc.)")
    print("=" * 50)
    app.run(debug=True, port=5000)