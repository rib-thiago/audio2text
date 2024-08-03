# app/processing.py

import ffmpeg
import tempfile
from pathlib import Path
import speech_recognition as sr
import os

def convert_to_wav(audio_file_path: Path, output_path: Path) -> None:
    try:
        ffmpeg.input(str(audio_file_path)).output(str(output_path)).run(quiet=True, overwrite_output=True)
    except ffmpeg.Error as e:
        print(f"Erro ao converter o arquivo de áudio: {e}")

def segment_audio(audio_file_path: Path) -> list[Path]:
    temp_dir = tempfile.mkdtemp()
    audio_file_path = Path(audio_file_path)
    probe = ffmpeg.probe(str(audio_file_path), select_streams='a', show_entries='format=duration', of='json')
    duration = float(probe['format']['duration'])
    segment_duration = 50
    segments = []
    start_time = 0

    while start_time < duration:
        end_time = min(start_time + segment_duration, duration)
        segment_file = Path(temp_dir) / f"segment_{start_time}_{end_time}.wav"
        ffmpeg.input(str(audio_file_path), ss=start_time, to=end_time).output(str(segment_file)).run(quiet=True, overwrite_output=True)
        segments.append(segment_file)
        start_time += segment_duration

    return segments

def transcribe_and_save(segments: list[Path], output_file: Path) -> None:
    recognizer = sr.Recognizer()
    with open(output_file, 'w') as file:
        for segment in segments:
            start_time = float(segment.stem.split('_')[1])
            end_time = float(segment.stem.split('_')[2])
            timestamp = f"{int(start_time // 3600):02}:{int((start_time % 3600) // 60):02}:{int(start_time % 60):02} - {int(end_time // 3600):02}:{int((end_time % 3600) // 60):02}:{int(end_time % 60):02}"
            try:
                with sr.AudioFile(str(segment)) as source:
                    audio_data = recognizer.record(source)
                    text = recognizer.recognize_google(audio_data, language="pt-BR")
                    file.write(f"{timestamp}\n{text}\n\n")
            except sr.UnknownValueError:
                file.write(f"{timestamp}\n[Áudio não reconhecido]\n\n")
            except sr.RequestError as e:
                file.write(f"{timestamp}\n[Erro de requisição: {e}]\n\n")
            finally:
                os.remove(segment)
