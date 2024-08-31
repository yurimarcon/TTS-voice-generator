import whisper
from TTS.api import TTS
import torch
from pydub import AudioSegment
from pydub.silence import detect_silence
import sys
import json
from googletrans import Translator
import os

inputAudio = sys.argv[1]
inputTranscriptText= sys.argv[2]
outputAudio = sys.argv[3]
source_lang=sys.argv[4]
dest_language=sys.argv[5]

tts_model = TTS(
    model_name="tts_models/multilingual/multi-dataset/xtts_v2", 
    progress_bar=False, 
    gpu=torch.cuda.is_available()
    )

with open(inputTranscriptText, 'r') as file:    
    result = json.load(file)

original_audio = AudioSegment.from_file(inputAudio)
silence_ranges = detect_silence(original_audio, min_silence_len=500, silence_thresh=-35)
initial_silence_duration = silence_ranges[0][1] if silence_ranges and silence_ranges[0][0] == 0 else 0

segments = result['segments']

#==================================================================================================
if source_lang == "en":
    translator = Translator()
    
    # Translate the segments and create audio usin TTS
    for idx, segment in enumerate(segments):
        original_text = segment['text']
        translated = translator.translate(original_text, src=source_lang, dest=dest_language)
        segment['translated_text'] = translated.text.replace(".", "")

        # Gerar áudio usando TTS
        tts_model.tts_to_file(
            text=segment['translated_text'], 
            speaker_wav=inputAudio, 
            language=dest_language, 
            file_path=f"../result/segment_{idx}.wav"
            )

#==================================================================================================
else:
    for idx, segment in enumerate(segments):
        original_text = segment['text']

        tts_model.tts_to_file(
            text=segment['text'], 
            # speaker_wav=inputAudio, 
            speaker_wav="../model_voice/model.wav", 
            language="en", 
            file_path=f"../result/segment_{idx}.wav"
            )

for idx, segment in enumerate(segments):
    audio = AudioSegment.from_file(f"../result/segment_{idx}.wav")
    duration_original = len(audio) / 1000  # Convertendo to miliseconds
    duration_target = segment['end'] - segment['start']
    speed_factor = duration_original / duration_target
    print(f"speed_factor {idx} {speed_factor}")
    if speed_factor < 0.5:
        speed_factor = 1
    # I used ffmpeg becouse in my tests did best performatic
    os.system(f'ffmpeg -i ../result/segment_{idx}.wav -filter:a "atempo={speed_factor}" ../result/segment_ajusted_{idx}.wav')

original_audio = AudioSegment.from_file(inputAudio)
silence_ranges = detect_silence(original_audio, min_silence_len=1000, silence_thresh=-35)
initial_silence_duration = silence_ranges[0][1] if silence_ranges and silence_ranges[0][0] == 0 else 0

final_audio = AudioSegment.silent(duration=initial_silence_duration)  # Add silence detected in start video

for idx, segment in enumerate(segments):
    adjusted_audio = AudioSegment.from_file(f"../result/segment_ajusted_{idx}.wav")
    segment_start = segment['start'] * 1000  # to milissegundos

    if final_audio.duration_seconds * 1000 < segment_start:
        silence_duration = segment_start - final_audio.duration_seconds * 1000
        final_audio += AudioSegment.silent(duration=silence_duration)

    final_audio += adjusted_audio

final_audio.export(outputAudio, format="wav")
