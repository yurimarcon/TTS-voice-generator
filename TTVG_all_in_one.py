import whisper
from googletrans import Translator
from TTS.api import TTS
import torch
from pydub import AudioSegment

# Inicializar o modelo TTS com uma voz específica
tts_model = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False, gpu=torch.cuda.is_available())

# Carregar o modelo Whisper
model = whisper.load_model("medium")  # Escolha o tamanho apropriado do modelo

# Transcrever o áudio com timestamps
result = model.transcribe("../result/audio.wav", language="pt", task="transcribe")

# Obter os segmentos transcritos
segments = result['segments']

translator = Translator()

# Traduzir os segmentos e gerar áudio usando TTS
for idx, segment in enumerate(segments):
    original_text = segment['text']
    translated = translator.translate(original_text, src='pt', dest='en')
    segment['translated_text'] = translated.text

    # Gerar áudio usando TTS
    tts_model.tts_to_file(text=segment['translated_text'], speaker_wav="../result/audio.wav", language="en", file_path=f"../result/segment_{idx}.wav")

# Ajustar a velocidade do áudio gerado para corresponder ao tempo do vídeo original
for idx, segment in enumerate(segments):
    tts_audio = AudioSegment.from_file(f"../result/segment_{idx}.wav")
    original_duration = (segment['end'] - segment['start']) * 1000  # Converter para milissegundos
    tts_duration = len(tts_audio)

    # Calcular fator de velocidade
    speed_factor = tts_duration / original_duration

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