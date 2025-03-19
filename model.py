from transformers import pipeline
from googletrans import Translator
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


plutchik_classifier = pipeline("text-classification", model="JuliusAlphonso/distilbert-plutchik")

vader_analyzer = SentimentIntensityAnalyzer()

def analyze_emotions(text):
    translator = Translator()
    translated = translator.translate(text)     
    text1 = translated.text
    print(text1) 
    result = {"input_text": text1, "plutchik_emotions": [], "vader_scores": {}}


    emotions = plutchik_classifier(text1)
    result["plutchik_emotions"] = [{emo["label"]: round(emo["score"], 2)} for emo in emotions]


    vader_scores = vader_analyzer.polarity_scores(text1)
    result["vader_scores"] = {key: round(value, 2) for key, value in vader_scores.items()}

    return result