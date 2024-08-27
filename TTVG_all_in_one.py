import whisper
from TTS.api import TTS
import torch
from pydub import AudioSegment
import json

# Obter o dispositivo (CPU ou GPU)
device = "cuda" if torch.cuda.is_available() else "cpu"

# Inicializar o modelo TTS com uma voz específica
# tts_model = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False, gpu=torch.cuda.is_available())
tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

# Carregar o modelo Whisper
model = whisper.load_model("small")  # Escolha o tamanho apropriado do modelo

# Transcrever o áudio com timestamps
result = model.transcribe(audio="../result/audio.wav", language="Portuguese", task="translate")
print (result)

# with open("../result/transcript.json", "a") as file:
#     file.write(json.dumps(result))

# Obter os segmentos transcritos
segments = result['segments']
print (segments)

tts_model.tts_to_file(text=result['text'], 
                    speaker_wav="../result/audio.wav", 
                    language="en", 
                    file_path=f"../result/x.wav",
                    split_sentences=True
                    )

# tts_new_audio = AudioSegment.from_file(f"../result/x.wav")
# original_audio = AudioSegment.from_file(f"../result/audio.wav")
# tts_duration = len(tts_new_audio)
# original_duration = len(original_audio)

# speed_factor = tts_duration / original_duration
# adjusted_audio = tts_new_audio.speedup(playback_speed=speed_factor)
# adjusted_audio.export(f"../result/new.wav", format="wav")

for idx, segment in enumerate(segments):
    tts_model.tts_to_file(text=segment['text'], 
                    speaker_wav="../result/audio.wav", 
                    language="en", 
                    file_path=f"../result/segment_{idx}.wav"
                    )

# Ajustar a velocidade do áudio gerado para corresponder ao tempo do vídeo original
for idx, segment in enumerate(segments):
    tts_audio = AudioSegment.from_file(f"../result/segment_{idx}.wav")
    original_duration = (segment['end'] - segment['start']) * 1000  # Converter para milissegundos
    tts_duration = len(tts_audio)

    # Calcular fator de velocidade
    speed_factor = tts_duration / original_duration
    print("tts_duration===>>>")
    print(tts_duration)
    print("original_duration===>>>")
    print(original_duration)

    # Ajustar velocidade
    adjusted_audio = tts_audio.speedup(playback_speed=speed_factor)

    # Exportar áudio ajustado
    adjusted_audio.export(f"../result/adjusted_segment_{idx}.wav", format="wav")

# Combinar os segmentos de áudio ajustados em um único arquivo de áudio final
final_audio = AudioSegment.silent(duration=0)

for idx, segment in enumerate(segments):
    adjusted_audio = AudioSegment.from_file(f"../result/adjusted_segment_{idx}.wav")

    # Calcular início do segmento atual
    segment_start = segment['start'] * 1000  # em milissegundos

    # Se houver um intervalo entre o final do último segmento e o início do atual, adicionar silêncio
    if final_audio.duration_seconds * 1000 < segment_start:
        silence_duration = segment_start - final_audio.duration_seconds * 1000
        final_audio += AudioSegment.silent(duration=silence_duration)

    final_audio += adjusted_audio

# Exportar áudio final
final_audio.export("../result/final_output_audio.wav", format="wav")