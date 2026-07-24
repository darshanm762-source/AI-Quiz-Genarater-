import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User Model for authentication and tracking history."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    quizzes = db.relationship('Quiz', backref='author', lazy=True, cascade="all, delete-orphan")
    results = db.relationship('Result', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat()
        }


class Quiz(db.Model):
    """Quiz Model representing a generated test session."""
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    topic = db.Column(db.String(150), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False, default='Medium')
    num_questions = db.Column(db.Integer, nullable=False, default=20)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete-orphan")
    results = db.relationship('Result', backref='quiz', lazy=True, cascade="all, delete-orphan")

    def to_dict(self, include_answers=False):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'topic': self.topic,
            'difficulty': self.difficulty,
            'num_questions': self.num_questions,
            'created_at': self.created_at.isoformat(),
            'questions': [q.to_dict(include_answer=include_answers) for q in self.questions]
        }


class Question(db.Model):
    """Question Model representing each multiple choice item."""
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.Text, nullable=False)
    option_b = db.Column(db.Text, nullable=False)
    option_c = db.Column(db.Text, nullable=False)
    option_d = db.Column(db.Text, nullable=False)
    answer = db.Column(db.String(255), nullable=False)  # Store exact answer text or option identifier
    explanation = db.Column(db.Text, nullable=True)

    def get_options_list(self):
        return [self.option_a, self.option_b, self.option_c, self.option_d]

    def to_dict(self, include_answer=False):
        data = {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'question': self.question,
            'options': [self.option_a, self.option_b, self.option_c, self.option_d],
            'explanation': self.explanation or f"The correct answer is {self.answer}."
        }
        if include_answer:
            data['answer'] = self.answer
        return data


class Result(db.Model):
    """Result Model to record user test submissions and grades."""
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    grade = db.Column(db.String(5), nullable=False)
    user_answers_json = db.Column(db.Text, nullable=True) # JSON string of submitted answers
    verification_code = db.Column(db.String(64), unique=True, default=lambda: str(uuid.uuid4())[:12].upper())
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'user_id': self.user_id,
            'score': self.score,
            'total_questions': self.total_questions,
            'percentage': round(self.percentage, 2),
            'grade': self.grade,
            'verification_code': self.verification_code,
            'completed_at': self.completed_at.isoformat(),
            'topic': self.quiz.topic if self.quiz else 'General Quiz',
            'difficulty': self.quiz.difficulty if self.quiz else 'Medium'
        }
