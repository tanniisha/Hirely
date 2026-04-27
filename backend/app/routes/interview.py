from flask import Blueprint, request, jsonify
from app.models.database import db, Interview, User, Question
from app.services.gemini_service import GeminiService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('interview', __name__, url_prefix='/api/interview')

try:
    gemini_service = GeminiService()
except Exception as e:
    logger.error(f'Failed to initialize GeminiService: {e}')
    gemini_service = None

@bp.route('/create', methods=['POST'])
def create_interview():

    try:
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'No JSON data provided'}), 400
        
        user_id = data.get('user_id')
        job_title = data.get('job_title')
        difficulty = data.get('difficulty', 'medium')
        
        if not user_id or not job_title:
            return jsonify({'status': 'error', 'message': 'user_id and job_title are required'}), 400
        
        logger.info(f'Creating interview for user {user_id}, job {job_title}')
        

        user = User.query.filter_by(id=user_id).first()
        if not user:
            user = User(id=user_id, name=data.get('name', 'Anonymous'), 
                       email=data.get('email', f'{user_id}@temp.com'))
            db.session.add(user)
            logger.info(f'Created new user: {user_id}')
        

        interview = Interview(
            user_id=user_id,
            job_title=job_title,
            difficulty=difficulty
        )
        db.session.add(interview)
        db.session.commit()
        
        logger.info(f'Interview created: {interview.id}')
        

        logger.info(f'Pre-generating 10 questions for interview {interview.id}')
        try:
            for q_num in range(1, 11):
                question_text = gemini_service.generate_question(
                    job_title,
                    difficulty,
                    q_num
                )
                question = Question(
                    interview_id=interview.id,
                    question_text=question_text,
                    question_number=q_num
                )
                db.session.add(question)
            db.session.commit()
            logger.info(f'All 10 questions pre-generated for interview {interview.id}')
        except Exception as e:
            logger.warning(f'Failed to pre-generate questions: {str(e)}. Will generate on-demand.')
        
        return jsonify({
            'status': 'success',
            'interview_id': interview.id,
            'job_title': interview.job_title,
            'difficulty': interview.difficulty
        }), 201
    except Exception as e:
        logger.error(f'Error creating interview: {str(e)}')
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400

@bp.route('/<interview_id>/next-question', methods=['GET'])
def get_next_question(interview_id):

    try:
        interview = Interview.query.get(interview_id)
        if not interview:
            return jsonify({'status': 'error', 'message': 'Interview not found'}), 404
        

        question = Question.query.filter_by(
            interview_id=interview_id,
            user_answer=None
        ).order_by(Question.question_number).first()
        
        if not question:
            return jsonify({'status': 'completed', 'message': 'All questions answered'}), 200
        
        logger.info(f'Retrieved question {question.question_number} for interview {interview_id}')
        
        return jsonify({
            'status': 'success',
            'question_id': question.id,
            'question_number': question.question_number,
            'question_text': question.question_text
        }), 200
    except Exception as e:
        logger.error(f'Error getting next question: {str(e)}')
        return jsonify({'status': 'error', 'message': str(e)}), 400

@bp.route('/submit-answer', methods=['POST'])
def submit_answer():

    try:
        if not gemini_service:
            return jsonify({'status': 'error', 'message': 'Gemini service not available'}), 500
        
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'No JSON data provided'}), 400
        
        question_id = data.get('question_id')
        user_answer = data.get('answer')
        
        if not question_id or not user_answer:
            return jsonify({'status': 'error', 'message': 'question_id and answer are required'}), 400
        
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'status': 'error', 'message': 'Question not found'}), 404
        
        logger.info(f'Processing answer for question {question_id}')
        

        question.user_answer = user_answer
        

        interview = question.interview
        evaluation_result = gemini_service.evaluate_answer(
            question.question_text,
            user_answer,
            interview.job_title
        )
        
        question.ai_evaluation = evaluation_result
        db.session.commit()
        
        logger.info(f'Answer evaluated for question {question_id}')
        
        return jsonify({
            'status': 'success',
            'evaluation': evaluation_result
        }), 200
    except Exception as e:
        logger.error(f'Error submitting answer: {str(e)}')
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400

@bp.route('/<interview_id>/end', methods=['POST'])
def end_interview(interview_id):

    try:
        interview = Interview.query.get(interview_id)
        if not interview:
            return jsonify({'status': 'error', 'message': 'Interview not found'}), 404
        
        logger.info(f'Ending interview {interview_id}')
        
        interview.status = 'completed'
        interview.completed_at = datetime.utcnow()
        

        questions = Question.query.filter_by(interview_id=interview_id).all()
        interview.score = len(questions) * 10  # Placeholder
        
        db.session.commit()
        
        logger.info(f'Interview {interview_id} ended with score {interview.score}')
        
        return jsonify({
            'status': 'success',
            'final_score': interview.score,
            'interview_id': interview.id
        }), 200
    except Exception as e:
        logger.error(f'Error ending interview: {str(e)}')
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400
