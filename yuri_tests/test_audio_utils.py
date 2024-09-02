import unittest
from pydub import AudioSegment
from audio_utils import get_speed_factory, process_text
import json

inputTranscriptText = "yuri_tests/data_tests/transcript.json"
inputAudioTest = "yuri_tests/data_tests/segment_0.wav"

with open(inputTranscriptText, 'r') as file:    
    result = json.load(file)

segments = result['segments']

class TestAudioUtils(unittest.TestCase):

    # Minor then speed_factory 0.9 make audio verry slow
    def test_get_speed_factory_small(self):
        segments[0]['start'] = 0
        segments[0]['end'] = 3.5
        speed_factor = get_speed_factory(segments[0], inputAudioTest)
        self.assertEqual(speed_factor, 0.9)

    # More then speed_factory 1.3 make audio verry fast
    def test_get_speed_factory_large(self):
        segments[0]['start'] = 0
        segments[0]['end'] = 2.3
        speed_factor = get_speed_factory(segments[0], inputAudioTest)
        self.assertEqual(speed_factor, 1.3)


if __name__ == '__main__':
    unittest.main()