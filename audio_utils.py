from pydub import AudioSegment
from pydub.silence import detect_silence
import os

def get_silence_ranges (inputAudio):
    original_audio = AudioSegment.from_file(inputAudio)
    return detect_silence(original_audio, min_silence_len=1000, silence_thresh=-35)

def get_initial_silence_duration (silence_ranges):
    return silence_ranges[0][1] if silence_ranges and silence_ranges[0][0] == 0 else 0

def get_speed_factory (segment_by_transcript, file_path_to_verify):
    audio = AudioSegment.from_file(file_path_to_verify)
    duration_segment = len(audio) / 1000  # Converting to miliseconds
    duration_transcipt = segment_by_transcript['end'] - segment_by_transcript['start']
    speed_factor = duration_segment / duration_transcipt
    print(f"speed_factor {segment_by_transcript['id']} {speed_factor}")
    if speed_factor < 0.9:
        speed_factor = 0.9
    elif speed_factor > 1.3:
        speed_factor = 1.3
    return speed_factor

def remove_silence_unecessery(audio_path):
    audio_did_ajusted = AudioSegment.from_file(audio_path)
    silence_ranges = detect_silence(audio_did_ajusted, min_silence_len=2000, silence_thresh=-35)
    for silence in silence_ranges:
        before_silence = audio_did_ajusted[:silence[0]]
        after_silence = audio_did_ajusted[silence[1]:]
        audio_without_silence = before_silence + after_silence
        audio_without_silence.export(audio_path, format="wav")

def put_silence_to_ajust_time (segment):
    audio_did_ajusted = AudioSegment.from_file(f"../result/segment_ajusted_{segment['id']}.wav")
    duration_audio_did_ajusted = len(audio_did_ajusted) / 1000
    duration_transcipt = segment['end'] - segment['start']
    print(f"{duration_audio_did_ajusted} > {duration_transcipt}")
    if duration_audio_did_ajusted < duration_transcipt:
        time_less = (duration_transcipt - duration_audio_did_ajusted) * 1000
        audio_espace_temp = AudioSegment.silent(duration=time_less)
        # audio_did_ajusted += audio_espace_temp
        audio_espace_temp += audio_did_ajusted
        audio_espace_temp.export(f"../result/segment_ajusted_{segment['id']}.wav", format="wav")

def ajust_time_segments ():
    original_audio = AudioSegment.from_file(f"../result/audio.wav")
    duration_original_audio = len(original_audio) / 1000
    output_audio = AudioSegment.from_file(f"../result/output.wav")
    duration_output_audio = len(output_audio) / 1000
    speed_factor = duration_output_audio / duration_original_audio
    os.system(f'ffmpeg -i ../result/output.wav -filter:a "atempo={speed_factor}" ../result/new_output.wav')
    os.remove(f"../result/output.wav")
    os.rename(f"../result/new_output.wav", "../result/output.wav")

def put_silence_in_segments (segment, idx, silence_ranges):
    for silence in silence_ranges:
        print(f"silence => {silence[0]}")
        print(segment['end'])
        if silence[0] < segment['end'] * 1000:
            silence_duration = silence[1] - silence[0]
            audio_espace_temp = AudioSegment.silent(duration=silence_duration)
            space_before = silence[0] - segment['start'] * 1000
            space_after = segment['end'] * 1000 - silence[1]

            audio = AudioSegment.from_file(f"../result/segment_ajusted_{idx}.wav")

            if space_before < space_after:
                print("space before")
                audio_espace_temp += audio
            else:
                print("space after")
                audio += audio_espace_temp
            
            silence_ranges.pop(0)
            audio.export(f"../result/segment_ajusted_{idx}.wav", format="wav")
            speed_factor = get_speed_factory (segment, f"../result/segment_{segment['id']}.wav")
            os.system(f'ffmpeg -i ../result/segment_ajusted_{idx}.wav -filter:a "atempo={speed_factor}" ../result/segment_ajusted_{idx}.wav')
            break