from flask import Blueprint, request, jsonify
from app.models.database import db, Interview, Question

bp = Blueprint('questions', __name__, url_prefix='/api/questions')

@bp.route('/<interview_id>', methods=['GET'])
def get_all_questions(interview_id):

    try:
        interview = Interview.query.get(interview_id)
        if not interview:
            return jsonify({'status': 'error', 'message': 'Interview not found'}), 404
        
        questions = Question.query.filter_by(interview_id=interview_id).all()
        
        questions_data = []
        for q in questions:
            questions_data.append({
                'id': q.id,
                'question_number': q.question_number,
                'question_text': q.question_text,
                'user_answer': q.user_answer,
                'score': q.score
            })
        
        return jsonify({
            'status': 'success',
            'total_questions': len(questions_data),
            'questions': questions_data
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@bp.route('/<question_id>', methods=['GET'])
def get_question_detail(question_id):

    try:
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'status': 'error', 'message': 'Question not found'}), 404
        
        return jsonify({
            'status': 'success',
            'id': question.id,
            'question_text': question.question_text,
            'question_number': question.question_number,
            'user_answer': question.user_answer,
            'ai_evaluation': question.ai_evaluation,
            'score': question.score
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
