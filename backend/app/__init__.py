from flask import Flask, jsonify
from flask_cors import CORS

import os
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    


    

    CORS(app)
    

    @app.errorhandler(Exception)
    def handle_error(error):
        logger.error(f'Error: {str(error)}')
        return jsonify({'status': 'error', 'message': str(error)}), 500
    

    try:
        from app.routes import resume_chat
        app.register_blueprint(resume_chat.bp)
        logger.info('Blueprints registered successfully')
    except Exception as e:
        logger.error(f'Blueprint registration failed: {e}')
        raise
    
    return app
