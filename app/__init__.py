from flask import Flask
from flask_cors import CORS
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize the app with the config
    config_class.init_app(app)
    
    CORS(app)
    
    from app.routes import bp
    app.register_blueprint(bp)
    
    return app