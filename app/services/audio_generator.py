from gtts import gTTS
from moviepy.editor import AudioFileClip
from flask import current_app
import os

def create_audio(text, filename):
   
    filename = os.path.basename(filename)
    

    full_path = os.path.join(current_app.config['OUTPUT_FOLDER'], filename)
    
   
    tts = gTTS(text, lang='en')
    tts.save(full_path)
    
   
    audio = AudioFileClip(full_path)
    return audio.volumex(1.5)  