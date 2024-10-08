import torch
from TTS.api import TTS
from pydub import AudioSegment
import sys, os

inputAudio = sys.argv[1]
inputTranscriptText = sys.argv[2]
outputAudio = sys.argv[3]

# Função para dividir o texto em partes menores com base no limite de caracteres
def split_text_by_characters(text, max_length=250):
    segments = []
    while len(text) > max_length:
        split_at = text.rfind(' ', 0, max_length)
        if split_at == -1:  # Caso não encontre um espaço, divide no limite exato
            split_at = max_length
        segments.append(text[:split_at])
        text = text[split_at:].strip()
    segments.append(text)  # Adiciona o último segmento
    return segments

# Carregar o conteúdo do arquivo transcrito
with open(inputTranscriptText, "r") as file:
    contentFile = file.read()

# Obter o dispositivo (CPU ou GPU)
device = "cuda" if torch.cuda.is_available() else "cpu"

# Inicializar o modelo TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

# Dividir o texto em partes menores com base no limite de caracteres
segments = split_text_by_characters(contentFile, max_length=250)

# Inicializar a lista para armazenar os segmentos de áudio
audio_segments = []
temp_audio = "../result/segment.wav"

# Gerar áudio para cada segmento e armazenar
for segment in segments:
    wav_segment_path = temp_audio
    tts.tts_to_file(text=segment, 
                    speaker_wav=inputAudio, 
                    language="en", 
                    file_path=wav_segment_path,
                    split_sentences=True)
    audio_segment = AudioSegment.from_wav(wav_segment_path)
    audio_segments.append(audio_segment)

# Combinar todos os segmentos de áudio
combined_audio = AudioSegment.silent(duration=0)
for segment in audio_segments:
    combined_audio += segment

# Calcular a diferença de duração entre o áudio original e o gerado
original_audio = AudioSegment.from_wav(inputAudio)
original_duration = len(original_audio)
generated_duration = len(combined_audio)
duration_difference = original_duration - generated_duration

# Ajustar a duração adicionando silêncios distribuídos uniformemente
if duration_difference > 0:
    print("duration_difference:")
    print(duration_difference)
    print("segments:")
    print(len(segments))
    silence_to_add = duration_difference / (len(segments))  # Distribui o silêncio entre os segmentos
    adjusted_audio = AudioSegment.silent(duration=0)
    for segment in audio_segments:
        adjusted_audio += segment + AudioSegment.silent(duration=silence_to_add)
else:
    adjusted_audio = combined_audio

# Exportar o áudio ajustado
adjusted_audio.export(outputAudio, format="wav")

os.remove(temp_audio)