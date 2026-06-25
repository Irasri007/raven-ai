from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle

# ── TRAINING DATA ──────────────────────────────────────
# Format: ("all phrases for this intent", "intent_name")
# Add more phrases = better accuracy
training_data = [
    ("hello hi namaste helo hey hy", "greet"),
    ("time samay baje kitne kya waqt", "get_time"),
    ("date tarikh aaj kal din mahina", "get_date"),
    ("music gaana song bajao chala gana sunao play track", "play_music"),
    ("youtube open kholo launch", "open_youtube"),
    ("google search karo dhundo find", "google_search"),
    ("wikipedia search wiki batao", "wikipedia_search"),
    ("translate hindi mein karo translation", "translate"),
    ("task add karo naya kaam todo reminder", "add_task"),
    ("tasks dikhao batao show kaam list pending", "show_tasks"),
    ("whatsapp message bhejo send", "whatsapp"),
    ("email mail bhejo send", "send_email"),
    ("open app kholo launch start", "open_app"),
    ("image banao generate photo tasveer create draw", "image_gen"),
    ("exit bye band stop alvida close quit", "exit"),
    ("raven batao bata question puchna ask what why how", "ask_ai"),
]

# ── EXPAND PHRASES INTO INDIVIDUAL TRAINING SAMPLES ────
texts, labels = [], []
for phrase, label in training_data:
    for word in phrase.split():
        texts.append(word)
        labels.append(label)

# ── BUILD AND TRAIN THE MODEL ──────────────────────────
model = Pipeline([
    ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))),
    ("clf", SGDClassifier(loss="hinge", max_iter=200, random_state=42)),
])
model.fit(texts, labels)

# ── SAVE THE MODEL ─────────────────────────────────────
with open("intent_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model trained and saved as intent_model.pkl!")