from flask import Blueprint, request, jsonify
from app.models.database import db, Interview, Question, Feedback
from app.services.gemini_service import GeminiService
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('feedback', __name__, url_prefix='/api/feedback')

try:
    gemini_service = GeminiService()
except Exception as e:
    logger.error(f'Failed to initialize GeminiService: {e}')
    gemini_service = None

@bp.route('/<interview_id>', methods=['GET'])
def get_feedback(interview_id):

    try:
        if not gemini_service:
            return jsonify({'status': 'error', 'message': 'Gemini service not available'}), 500
        
        interview = Interview.query.get(interview_id)
        if not interview:
            return jsonify({'status': 'error', 'message': 'Interview not found'}), 404
        
        if interview.status != 'completed':
            return jsonify({'status': 'error', 'message': 'Interview not yet completed'}), 400
        
        feedback = Feedback.query.filter_by(interview_id=interview_id).first()
        
        if not feedback:
            logger.info(f'Generating feedback for interview {interview_id}')
            

            questions = Question.query.filter_by(interview_id=interview_id).all()
            answers = [q.user_answer for q in questions]
            scores = [q.score or 0 for q in questions]
            
            feedback_text = gemini_service.generate_overall_feedback(
                interview.job_title,
                answers,
                scores
            )
            
            feedback = Feedback(
                interview_id=interview_id,
                overall_feedback=feedback_text,
                strengths='',
                areas_for_improvement=''
            )
            db.session.add(feedback)
            db.session.commit()
            
            logger.info(f'Feedback generated for interview {interview_id}')
        
        return jsonify({
            'status': 'success',
            'interview_id': interview_id,
            'final_score': interview.score,
            'overall_feedback': feedback.overall_feedback,
            'strengths': feedback.strengths,
            'areas_for_improvement': feedback.areas_for_improvement
        }), 200
    except Exception as e:
        logger.error(f'Error getting feedback: {str(e)}')
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400
