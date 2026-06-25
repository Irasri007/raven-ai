from transformers import pipeline

# Load karo ek baar — startup pe thoda time lagta hai
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
)

def get_mood(text):
    """
    Returns: 'positive', 'negative', ya 'neutral'
    """
    try:
        result = sentiment_analyzer(text[:512])[0]  # max 512 chars
        label = result["label"].lower()
        score = result["score"]

        print(f"😊 Mood detected: {label} (confidence: {score:.2f})")
        return label
    except Exception as e:
        print(f"Sentiment error: {e}")
        return "neutral"  # fallback


# Test karo file directly run karke
if __name__ == "__main__":
    test_phrases = [
        "mujhe bahut khushi ho rahi hai",
        "main bahut thak gaya hoon aaj",
        "time kya hua",
        "i am so happy today",
        "yaar bohot bura din tha",
    ]
    for phrase in test_phrases:
        mood = get_mood(phrase)
        print(f"  '{phrase}' → {mood}\n")