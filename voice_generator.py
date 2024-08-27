# import torch
# from TTS.api import TTS

# # Read the file content transcripted
# file = open("../result/transcript.txt", "r")
# contentFile = file.read()
# file.close()

# # Get device
# device = "cuda" if torch.cuda.is_available() else "cpu"

# # List available 🐸TTS models
# print(TTS().list_models())

# # Init TTS
# tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

# # # Run TTS
# # # ❗ Since this model is multi-lingual voice cloning model, we must set the target speaker_wav and language
# # # Text to speech list of amplitude values as output
# # wav = tts.tts(text=contentFile, speaker_wav="../result/audio.wav", language="pt")
# wav = tts.tts(text=contentFile, speaker_wav="../result/audio.wav", language="en")

# # # Text to speech to a file
# # tts.tts_to_file(text=contentFile, speaker_wav="../result/audio.wav", language="pt", file_path="../result/output.wav")
# tts.tts_to_file(text=contentFile, speaker_wav="../result/audio.wav", language="en", file_path="../result/output.wav")






import torch
from TTS.api import TTS
from pydub import AudioSegment
import sys, os

inputAudio = sys.argv[1]
inputTranscriptText= sys.argv[2]
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
path_segment = "../result/segment.wav"

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

# Combinar todos os segmentos de áudio
combined_audio = AudioSegment.silent(duration=0)
for segment in audio_segments:
    combined_audio += segment + AudioSegment.silent(duration=500)  # Adiciona uma pausa de 500ms entre segmentos

# Exportar o áudio temporario combinado
combined_audio.export(outputAudio, format="wav")

os.remove(path_segment)

# combined_audio.export("../result/temp.wav", format="wav")

# temp_audio = AudioSegment.from_file(f"../result/temp.wav")
# original_audio = AudioSegment.from_file(inputAudio)
# tts_duration = len(temp_audio)
# original_duration = len(original_audio)

# speed_factor = tts_duration / original_duration
# adjusted_audio = temp_audio.speedup(playback_speed=speed_factor)

# # Exportar o áudio temporario combinado
# adjusted_audio.export(outputAudio, format="wav")
