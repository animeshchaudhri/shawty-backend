import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    TIMER_SOUND_PATH = os.environ.get('TIMER_SOUND_PATH')
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    OUTPUT_FOLDER = os.environ.get('OUTPUT_FOLDER') or os.path.join(BASE_DIR, 'output')
    
    @staticmethod
    def init_app(app):
        # Ensure the output directory exists
        os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
        app.logger.info(f"Output folder set to: {Config.OUTPUT_FOLDER}")
       
        # Set the full path for the timer sound
       
        
        # Set the full path for the output folder
        Config.OUTPUT_FOLDER = os.path.join(app.root_path, Config.OUTPUT_FOLDER)
       