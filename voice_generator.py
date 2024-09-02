import whisper
from TTS.api import TTS
import torch
from pydub import AudioSegment
from pydub.silence import detect_silence
import sys
import json
# from googletrans import Translator
import os
import glob

from audio_utils import get_silence_ranges, get_initial_silence_duration, get_speed_factory, remove_silence_unecessery, put_silence_to_ajust_time, ajust_time_segments
from translate_utils import translate_text

inputAudio = sys.argv[1]
inputTranscriptText= sys.argv[2]
outputAudio = sys.argv[3]
source_lang=sys.argv[4]
dest_language=sys.argv[5]

# translator = Translator()

########################################################

# def translate_text (segment):
#     translated = translator.translate(
#         segment['text'], 
#         src=source_lang,
#         dest=dest_language
#         )
        
#     return translated.text.replace(".", "")

def generate_other_lenguages_audio_segments (segments):
    for idx, segment in enumerate(segments):
        text = translate_text(segment, source_lang, dest_language)
        tts_model.tts_to_file(
            text=text, 
            speaker_wav=inputAudio, 
            language=dest_language, 
            file_path=f"../result/segment_{idx}.wav"
            )
        print(f"{idx+1}/{len(segments)} segments created.")

def generate_english_audio_segments (segments):
    for idx, segment in enumerate(segments):
        tts_model.tts_to_file(
            text=segment['text'], 
            # speaker_wav=inputAudio, 
            speaker_wav="../model_voice/model.wav", 
            language="en", 
            file_path=f"../result/segment_{idx}.wav"
            )
        print(f"{idx+1}/{len(segments)} segments created.")

def generate_segments_ajusted (segment, initial_file, ajusted_file):
    speed_factor = get_speed_factory(segment, initial_file)
    print(f"speed_factor ===>>>>>{speed_factor}")
    # I used ffmpeg becouse in my tests did best performatic
    os.system(f'ffmpeg -i {initial_file} -filter:a "atempo={speed_factor}" {ajusted_file}')
    remove_silence_unecessery(ajusted_file)
    put_silence_to_ajust_time(segment)

def uniteding_segments_ajusted (segments, final_audio):
    for idx, segment in enumerate(segments):
        adjusted_audio = AudioSegment.from_file(f"../result/segment_ajusted_{idx}.wav")
        final_audio += adjusted_audio
    return final_audio

def generate_final_audio(segments, initial_silence_duration):
    final_audio = AudioSegment.silent(duration=initial_silence_duration)
    final_audio = uniteding_segments_ajusted(segments, final_audio)
    final_audio.export(outputAudio, format="wav")

def remove_files_after_process():
    files = glob.glob("..result/segment*")
    for file in files:
        os.remove(file)

######################################################################

tts_model = TTS(
    model_name="tts_models/multilingual/multi-dataset/xtts_v2", 
    progress_bar=False, 
    gpu=torch.cuda.is_available()
    )

with open(inputTranscriptText, 'r') as file:    
    result = json.load(file)

segments = result['segments']

if source_lang == "en":
    generate_other_lenguages_audio_segments(segments)
    pass
else:
    # generate_english_audio_segments(segments)
    pass
    
silence_ranges = get_silence_ranges(inputAudio)
initial_silence_duration = get_initial_silence_duration(silence_ranges)

for idx, segment in enumerate(segments):
    generate_segments_ajusted(
        segment, 
        f"../result/segment_{idx}.wav", 
        f"../result/segment_ajusted_{idx}.wav"
        )

generate_final_audio(segments, initial_silence_duration)
ajust_time_segments()
remove_files_after_process()
