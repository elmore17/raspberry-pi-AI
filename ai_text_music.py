import os
import whisper
import xlsxwriter

def model_convert_audio_to_text():
    model = whisper.load_model("base")
    result = model.transcribe('audio.wav', verbose = True)
    return result["text"]

def create_workbook_with_text():
    filename = "text_music.xlsx"
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'text_music')
    worksheet.write('A2', model_convert_audio_to_text())
    workbook.close()

model_convert_audio_to_text()