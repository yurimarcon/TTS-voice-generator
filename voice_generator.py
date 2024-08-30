import whisper
from TTS.api import TTS
import torch
from pydub import AudioSegment
from pydub.silence import detect_silence
import sys
import json
from googletrans import Translator

inputAudio = sys.argv[1]
inputTranscriptText= sys.argv[2]
outputAudio = sys.argv[3]

tts_model = TTS(
    model_name="tts_models/multilingual/multi-dataset/xtts_v2", 
    progress_bar=False, 
    gpu=torch.cuda.is_available()
    )

with open(inputTranscriptText, 'r') as file:    
    result = json.load(file)

original_audio = AudioSegment.from_file(inputAudio)
silence_ranges = detect_silence(original_audio, min_silence_len=500, silence_thresh=-50)
initial_silence_duration = silence_ranges[0][1] if silence_ranges and silence_ranges[0][0] == 0 else 0

segments = result['segments']


#==================================================================================================

translator = Translator()

# Traduzir os segmentos e gerar áudio usando TTS
for idx, segment in enumerate(segments):
    original_text = segment['text']
    translated = translator.translate(original_text, src='en', dest='pt')
    segment['translated_text'] = translated.text

    # Gerar áudio usando TTS
    tts_model.tts_to_file(
        text=segment['translated_text'], 
        speaker_wav=inputAudio, 
        language="pt", 
        file_path=f"../result/segment_{idx}.wav"
        )

#==================================================================================================

# for idx, segment in enumerate(segments):
#     original_text = segment['text']

#     tts_model.tts_to_file(
#         text=segment['text'], 
#         speaker_wav=inputAudio, 
#         # speaker_wav="../result/model.wav", 
#         language="pt", 
#         # language="en", 
#         file_path=f"../result/segment_{idx}.wav"
#         )

final_audio = AudioSegment.silent(duration=initial_silence_duration)  # Add silence detected in start video

for idx, segment in enumerate(segments):
    adjusted_audio = AudioSegment.from_file(f"../result/segment_{idx}.wav")
    segment_start = segment['start'] * 1000  # to milissegundos
    if final_audio.duration_seconds * 1000 < segment_start:
        silence_duration = segment_start - final_audio.duration_seconds * 1000
        final_audio += AudioSegment.silent(duration=silence_duration)

    final_audio += adjusted_audio

final_audio.export(outputAudio, format="wav")
