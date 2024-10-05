from gtts import gTTS
from pydub import AudioSegment
from pydub.effects import speedup
import os
from TTS.api import TTS


audio_folder = "audios"

def generate_audio_tts(file_name, sentence):
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    audio_file = os.path.join(audio_folder, "{}.wav".format(file_name))

    # generate speech by cloning a voice using default settings
    if not os.path.exists(audio_file):
        tts.tts_to_file(text=sentence,
            file_path=audio_file,
            speaker="Ana Florence",
            language="en",
        )
    return audio_file

def generate_audio_gtts(file_name, sentence, speed=1.0):
    audio_file = os.path.join(audio_folder, "{}_gtts.mp3".format(file_name))  # Save audio in the "audios" folder

    if not os.path.exists(audio_file):
        tts = gTTS(text=sentence, lang='en', slow=False)
        tts.GOOGLE_TTS_MAX_CHARS = 200
        tts.save(audio_file)

    if speed == 1.0:
        return audio_file

    sped_up_audio_file = os.path.join(audio_folder, f"{file_name}_gtts_fast.mp3")
    if os.path.exists(sped_up_audio_file):
        return sped_up_audio_file
    # Load the audio file using pydub
    audio_segment = AudioSegment.from_file(audio_file)

    # Speed up the audio by 10%
    audio_segment = speedup(audio_segment, playback_speed=speed)

    # Export the adjusted audio
    audio_segment.export(sped_up_audio_file, format="mp3")
    return sped_up_audio_file
