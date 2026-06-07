from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics
from groq import Groq

from app.config import Config
from app.db import init_db
from app.routes.forecast import forecast_bp
from app.routes.operations import operations_bp
from app.routes.settings import settings_bp
from app.routes.voice_api import voice_api_bp, init_voice_api


def create_app():
    flask_app = Flask(__name__,
                      template_folder='../templates',
                      static_folder='../static')
    flask_app.config['SECRET_KEY'] = Config.SECRET_KEY
    
    # Prometheus metrics
    PrometheusMetrics(flask_app)
    
    # Groq client for voice features
    if Config.GROQ_API_KEY:
        groq_client = Groq(api_key=Config.GROQ_API_KEY)
        init_voice_api(groq_client)
    
    # Initialize database
    with flask_app.app_context():
        init_db()
    
    # Register blueprints
    flask_app.register_blueprint(forecast_bp)
    flask_app.register_blueprint(operations_bp)
    flask_app.register_blueprint(settings_bp)
    flask_app.register_blueprint(voice_api_bp)
    
    return flask_app
