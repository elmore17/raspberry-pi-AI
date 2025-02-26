import os
import torch
import whisper
import xlsxwriter

from transformers import pipeline

# def model_convert_audio_to_text():
#     try:
#         model = whisper.load_model("base")
#         result = model.transcribe(r'C:\Users\Danila\Downloads\MORGENSHTERN_-_POVOD_79042608.mp3', fp16=False)
#         print(result["text"])
#     except Exception as e:
#         print(f"An error occurred: {e}")

# def create_workbook_with_text():
#     filename = "text_music.xlsx"
#     workbook = xlsxwriter.Workbook(filename)
#     worksheet = workbook.add_worksheet()
#     worksheet.write('A1', 'text_music')
#     worksheet.write('A2', model_convert_audio_to_text())
#     workbook.close()

# model_convert_audio_to_text()


####DONE
# device = "cuda" if torch.cuda.is_available() else "cpu"
# print(f"Using device: {device}")
# model = whisper.load_model("base").to(device)  # Можно выбрать модель: tiny, base, small, medium, large
# result = model.transcribe("MORGENSHTERN.mp3")
# print(result["text"])


classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

def moderate_text(text):
    result = classifier(text)[0]
    if result['label'] == 'NEGATIVE' and result['score'] > 0.9:
        print(result)
        return False  # Текст считается негативным
    return True  # Текст прошел модерацию

# Пример использования
text = "Я уже целец мер, бывшая права, ну как всегда. Здесь не добросто полот сайте сумма."
if moderate_text(text):
    print("Текст прошел модерацию.")
else:
    print("Текст не прошел модерацию.")