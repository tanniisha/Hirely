from flask import Blueprint, request, jsonify
from app.services.gemini_service import GeminiService
import PyPDF2
import io
import os
import tempfile

bp = Blueprint('resume_chat', __name__, url_prefix='/api/resume-chat')
gemini_service = GeminiService()

@bp.route('/upload', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    try:

        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                
        if not text.strip():
            return jsonify({'error': 'Could not extract text from PDF'}), 400
            

        first_message = gemini_service.analyze_resume_and_start(text)
        
        return jsonify({
            'resume_text': text,
            'message': first_message
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    resume_text = data.get('resume_text')
    history = data.get('history', [])
    
    if not resume_text:
        return jsonify({'error': 'Resume text is required'}), 400
        
    try:
        next_message = gemini_service.continue_interview_chat(resume_text, history)
        return jsonify({
            'message': next_message
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({'error': 'No audio file part'}), 400
    
    audio_file = request.files['file']
    if audio_file.filename == '':
        return jsonify({'error': 'No selected audio file'}), 400
        
    try:

        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
            audio_file.save(tmp.name)
            tmp_path = tmp.name
            
        try:
            transcript = gemini_service.transcribe_audio(tmp_path)
            return jsonify({'transcript': transcript})
        finally:

            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500
