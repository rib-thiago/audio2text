from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from audio2text.processing import convert_to_wav, segment_audio, transcribe_and_save
import shutil
import os

app = FastAPI()

TEMP_DIR = 'temp'

app.mount("/static", StaticFiles(directory="audio2text/static"), name="static")

@app.post("/upload/")
async def upload_audio(file: UploadFile = File(...)):
    # Cria diretório temporário se não existir
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    # Salva o arquivo de áudio
    file_path = Path(TEMP_DIR) / file.filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Converte para WAV se necessário
    wav_path = Path(TEMP_DIR) / file.filename.replace(file.filename.split('.')[-1], 'wav')
    if file_path.suffix.lower() != '.wav':
        convert_to_wav(file_path, wav_path)
        audio_path = wav_path
    else:
        audio_path = file_path

    # Segmenta o áudio e transcreve
    segments = segment_audio(audio_path)
    transcription_path = Path(TEMP_DIR) / "transcription.txt"
    transcribe_and_save(segments, transcription_path)

    # Limpeza dos arquivos temporários
    os.remove(file_path)
    if file_path != wav_path:
        os.remove(wav_path)

    return JSONResponse(content={"message": "Áudio processado com sucesso", "transcription_file": str(transcription_path)})

@app.get("/transcription/")
async def get_transcription():
    transcription_path = Path(TEMP_DIR) / "transcription.txt"
    if transcription_path.exists():
        with open(transcription_path, 'r') as file:
            content = file.read()
        return {"transcription": content}
    else:
        return JSONResponse(status_code=404, content={"message": "Transcrição não encontrada"})

@app.post("/save/")
async def save_transcription(transcription: dict):
    transcription_path = Path(TEMP_DIR) / "transcription.txt"
    if transcription_path.exists():
        with open(transcription_path, 'w') as file:
            file.write(transcription.get("transcription", ""))
        return {"message": "Transcrição salva com sucesso"}
    else:
        return JSONResponse(status_code=404, content={"message": "Transcrição não encontrada"})

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    with open("templates/index.html") as f:
        return HTMLResponse(content=f.read())
