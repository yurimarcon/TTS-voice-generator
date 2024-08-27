import whisper
from pydub import AudioSegment
from pydub.silence import detect_silence
from TTS.api import TTS
import numpy as np
import torch

# Carregar o arquivo de áudio original
audio = AudioSegment.from_wav("../result/audio.wav")

# Detectar os trechos de silêncio
silence_ranges = detect_silence(audio, min_silence_len=1000, silence_thresh=-50)
print(silence_ranges)

# Carregar o modelo Whisper
model = whisper.load_model("medium")
result = model.transcribe("../result/audio.wav", language="Portuguese", task="translate")

# Inicializar o modelo TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

# Crie um novo áudio com os silêncios preservados
final_audio = AudioSegment.silent(duration=0)

for idx, segment in enumerate(result['segments']):
    translated_text = segment['text']
    

    wav_segment_path = "../result/{idx}_audio.wav"
    tts.tts_to_file(text=segment, 
                    speaker_wav=inputAudio, 
                    language="en", 
                    file_path=wav_segment_path,
                    split_sentences=True)
    audio_segment = AudioSegment.from_wav(wav_segment_path)
    audio_segments.append(audio_segment)
    
    # Adicionar o áudio traduzido ao áudio final
    final_audio += audio_segments
    
    # Verificar se há um intervalo de silêncio a ser preservado
    if idx < len(silence_ranges):
        silence_start, silence_end = silence_ranges[idx]
        silence_duration = silence_end - silence_start
        
        # Adicionar silêncio após o segmento traduzido
        final_audio += AudioSegment.silent(duration=silence_duration)

# Exportar o áudio final
final_audio.export("../result/new_audio.wav", format="wav")








# Gerar áudio para cada segmento e armazenar
for segment in segments:
    wav_segment_path = path_segment
    tts.tts_to_file(text=segment, 
                    speaker_wav=inputAudio, 
                    language="en", 
                    file_path=wav_segment_path,
                    split_sentences=True)
    audio_segment = AudioSegment.from_wav(wav_segment_path)
    audio_segments.append(audio_segment)






# from pydub import AudioSegment
# from TTS.api import TTS

# # Inicializar o modelo TTS
# tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

# # Crie um novo áudio com os silêncios preservados
# final_audio = AudioSegment.silent(duration=0)

# for idx, segment in enumerate(result['segments']):
#     translated_text = segment['translated_text']
    
#     # Gerar o áudio para o texto traduzido
#     wav = tts.tts(text=translated_text, speaker_wav="../result/audio.wav", language="en")
    
#     # Convertendo para um AudioSegment
#     tts_audio = AudioSegment(wav)
    
#     # Adicionar o áudio traduzido ao áudio final
#     final_audio += tts_audio
    
#     # Verificar se há um intervalo de silêncio a ser preservado
#     if idx < len(silence_ranges):
#         silence_start, silence_end = silence_ranges[idx]
#         silence_duration = silence_end - silence_start
        
#         # Adicionar silêncio após o segmento traduzido
#         final_audio += AudioSegment.silent(duration=silence_duration)

# # Exportar o áudio final
# final_audio.export("../result/final_output_audio.wav", format="wav")