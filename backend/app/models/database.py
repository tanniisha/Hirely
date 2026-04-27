from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    interviews = db.relationship('Interview', backref='user', cascade='all, delete-orphan')

class Interview(db.Model):
    __tablename__ = 'interviews'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    job_title = db.Column(db.String(255), nullable=False)
    difficulty = db.Column(db.String(50), default='medium')  
    status = db.Column(db.String(50), default='in_progress')  
    score = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    questions = db.relationship('Question', backref='interview', cascade='all, delete-orphan')
    feedback = db.relationship('Feedback', backref='interview', cascade='all, delete-orphan')

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_id = db.Column(db.String(36), db.ForeignKey('interviews.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_number = db.Column(db.Integer, nullable=False)
    user_answer = db.Column(db.Text, nullable=True)
    ai_evaluation = db.Column(db.Text, nullable=True)
    score = db.Column(db.Float, nullable=True)
    audio_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_id = db.Column(db.String(36), db.ForeignKey('interviews.id'), nullable=False)
    overall_feedback = db.Column(db.Text, nullable=False)
    strengths = db.Column(db.Text, nullable=False)
    areas_for_improvement = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def init_db():
    db.create_all()
