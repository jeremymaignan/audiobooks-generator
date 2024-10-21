import os

from gtts import gTTS
from pydub import AudioSegment
from pydub.effects import speedup

audio_folder = "audios"

def generate_audio_gtts(file_name, sentence, speed=1.0):
    audio_file = os.path.join(audio_folder, "{}.mp3".format(file_name))  # Save audio in the "audios" folder

    if not os.path.exists(audio_file):
        tts = gTTS(text=sentence, lang='en', slow=False)
        tts.GOOGLE_TTS_MAX_CHARS = 200
        tts.save(audio_file)

    if speed == 1.0:
        return audio_file

    sped_up_audio_file = os.path.join(audio_folder, f"{file_name}_fast.mp3")
    if os.path.exists(sped_up_audio_file):
        return sped_up_audio_file
    # Load the audio file using pydub
    audio_segment = AudioSegment.from_file(audio_file)

    # Speed up the audio by 10%
    audio_segment = speedup(audio_segment, playback_speed=speed)

    # Export the adjusted audio
    audio_segment.export(sped_up_audio_file, format="mp3")
    return sped_up_audio_file
