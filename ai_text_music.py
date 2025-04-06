import os
import torch
import whisper
import xlsxwriter

from transformers import pipeline

    
####DONE

def model_convert_audio_to_text(filepath):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    model = whisper.load_model("base").to(device)  # Можно выбрать модель: tiny, base, small, medium, large
    result = model.transcribe(filepath)
    text = result["text"]
    return text

# classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")
def moderate_text(text): 
    classifier = pipeline(
        "text-classification", 
        model="yiyanghkust/finbert-tone",
        device=0 if torch.cuda.is_available() else -1
    )
    result = classifier(text)[0]
    if result['label'] == 'NEGATIVE' and result['score'] > 0.9:
        print(result)
        return False  # Текст считается негативным
    return True  # Текст прошел модерацию