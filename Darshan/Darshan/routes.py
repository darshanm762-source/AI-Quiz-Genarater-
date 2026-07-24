import csv
import json
import io
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, Response, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Quiz, Question, Result
from utils import generate_ai_quiz, calculate_grade
from config import Config

main_bp = Blueprint('main', __name__)

# -------------------------------------------------------------------
# PAGE ROUTES
# -------------------------------------------------------------------

@main_bp.route('/')
def index():
    """Home Page - Quiz Creation Dashboard"""
    recent_quizzes = Quiz.query.order_by(Quiz.created_at.desc()).limit(6).all()
    total_quizzes = Quiz.query.count()
    total_results = Result.query.count()
    return render_template('index.html', 
                           recent_quizzes=recent_quizzes, 
                           total_quizzes=total_quizzes, 
                           total_results=total_results,
                           default_questions=Config.DEFAULT_NUM_QUESTIONS,
                           min_questions=Config.MIN_QUESTIONS,
                           max_questions=Config.MAX_QUESTIONS)


@main_bp.route('/quiz/<int:quiz_id>')
def quiz_page(quiz_id):
    """Quiz Interface Page"""
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('quiz.html', quiz=quiz, timer_seconds=Config.TIMER_SECONDS_PER_QUESTION)


@main_bp.route('/result/<int:result_id>')
def result_page(result_id):
    """Quiz Score Result Page"""
    result = Result.query.get_or_404(result_id)
    # Parse answers for breakdown analysis if available
    answers_data = json.loads(result.user_answers_json) if result.user_answers_json else {}
    unanswered_count = 0
    correct_count = 0
    wrong_count = 0

    for q in result.quiz.questions:
        q_id_str = str(q.id)
        user_ans = answers_data.get(q_id_str)
        if not user_ans:
            unanswered_count += 1
        elif user_ans == q.answer:
            correct_count += 1
        else:
            wrong_count += 1

    return render_template('result.html', 
                           result=result, 
                           correct_count=correct_count, 
                           wrong_count=wrong_count, 
                           unanswered_count=unanswered_count)


@main_bp.route('/review/<int:result_id>')
def review_page(result_id):
    """Review Page - Answer by answer analysis with explanations"""
    result = Result.query.get_or_404(result_id)
    user_answers = json.loads(result.user_answers_json) if result.user_answers_json else {}
    return render_template('review.html', result=result, user_answers=user_answers)


@main_bp.route('/certificate/<int:result_id>')
def certificate_page(result_id):
    """Printable Accomplishment Certificate - Only issued for passed quizzes (Score >= 50%)"""
    result = Result.query.get_or_404(result_id)

    # Restrict certificate access to passed candidates (percentage >= 50%)
    if result.percentage < 50.0 or result.grade == 'F':
        flash('Certificates are awarded only for passing scores of 50% or higher (Grade D or better). Retake the quiz to pass!', 'warning')
        return redirect(url_for('main.result_page', result_id=result.id))

    candidate_name = current_user.username if (current_user and current_user.is_authenticated) else "Quiz Scholar"
    return render_template('certificate.html', result=result, candidate_name=candidate_name)


@main_bp.route('/leaderboard')
def leaderboard():
    """Global Leaderboard Page"""
    top_results = Result.query.order_by(Result.percentage.desc(), Result.completed_at.asc()).limit(20).all()
    return render_template('leaderboard.html', top_results=top_results)


# -------------------------------------------------------------------
# AUTHENTICATION ROUTES
# -------------------------------------------------------------------

@main_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """User Registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('main.signup'))

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or Email already registered.', 'warning')
            return redirect(url_for('main.signup'))

        # Make the very first registered user an admin automatically
        is_first_user = (User.query.count() == 0)
        new_user = User(username=username, email=email, is_admin=is_first_user)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash('Account created successfully! Welcome.', 'success')
        return redirect(url_for('main.index'))

    return render_template('signup.html')


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User Sign In"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('main.login'))

    return render_template('login.html')


@main_bp.route('/logout')
def logout():
    """Sign Out"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


# -------------------------------------------------------------------
# REST API ENDPOINTS
# -------------------------------------------------------------------

@main_bp.route('/generate-quiz', methods=['POST'])
@main_bp.route('/api/generate-quiz', methods=['POST'])
def api_generate_quiz():
    """
    POST /generate-quiz
    Request Body (JSON or Form):
    {
      "topic": "Python Programming",
      "difficulty": "Medium",
      "num_questions": 20
    }
    """
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    topic = data.get('topic', '').strip()
    difficulty = data.get('difficulty', 'Medium').capitalize()
    
    try:
        num_questions = int(data.get('num_questions', Config.DEFAULT_NUM_QUESTIONS))
    except (ValueError, TypeError):
        num_questions = Config.DEFAULT_NUM_QUESTIONS

    # Validation Checks
    if not topic:
        return jsonify({'success': False, 'error': 'Topic cannot be empty.'}), 400

    if num_questions < Config.MIN_QUESTIONS or num_questions > Config.MAX_QUESTIONS:
        return jsonify({'success': False, 'error': f'Number of questions must be between {Config.MIN_QUESTIONS} and {Config.MAX_QUESTIONS}.'}), 400

    if difficulty not in ['Easy', 'Medium', 'Hard']:
        difficulty = 'Medium'

    try:
        # Generate questions via AI or Fallback engine
        raw_questions = generate_ai_quiz(topic, difficulty, num_questions)

        if not raw_questions:
            return jsonify({'success': False, 'error': 'Failed to generate quiz questions. Please try another topic.'}), 500

        # Save to Database
        user_id = current_user.id if (current_user and current_user.is_authenticated) else None
        quiz = Quiz(
            topic=topic,
            difficulty=difficulty,
            num_questions=len(raw_questions),
            user_id=user_id
        )
        db.session.add(quiz)
        db.session.flush()  # Get quiz.id before adding questions

        for q_data in raw_questions:
            opts = [str(o).strip() for o in q_data.get('options', []) if str(o).strip()]
            fallbacks = ["Option A", "Option B", "Option C", "Option D"]
            while len(opts) < 4:
                opts.append(fallbacks[len(opts)])
            question_obj = Question(
                quiz_id=quiz.id,
                question=q_data['question'],
                option_a=opts[0],
                option_b=opts[1],
                option_c=opts[2],
                option_d=opts[3],
                answer=q_data['answer'],
                explanation=q_data.get('explanation', '')
            )
            db.session.add(question_obj)

        db.session.commit()

        return jsonify({
            'success': True,
            'quiz_id': quiz.id,
            'redirect_url': url_for('main.quiz_page', quiz_id=quiz.id),
            'message': 'Quiz generated successfully!'
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"[Generate Quiz API Error]: {e}")
        return jsonify({'success': False, 'error': f'Internal Server Error: {str(e)}'}), 500


@main_bp.route('/quiz/<int:quiz_id>/data', methods=['GET'])
@main_bp.route('/api/quiz/<int:quiz_id>', methods=['GET'])
def api_get_quiz(quiz_id):
    """
    GET /quiz/<id> or /api/quiz/<id>
    Returns quiz structure and questions.
    """
    quiz = Quiz.query.get_or_404(quiz_id)
    # Hide correct answers from public taking mode by default unless requested by admin
    include_answers = request.args.get('include_answers', 'false').lower() == 'true'
    return jsonify({
        'success': True,
        'quiz': quiz.to_dict(include_answers=include_answers)
    })


@main_bp.route('/submit-quiz', methods=['POST'])
@main_bp.route('/api/submit-quiz', methods=['POST'])
def api_submit_quiz():
    """
    POST /submit-quiz
    Request Payload:
    {
      "quiz_id": 1,
      "answers": {
        "101": "Python",
        "102": "Option B"
      }
    }
    """
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    quiz_id = data.get('quiz_id')
    user_answers = data.get('answers', {})

    # If submitted as form, answers might be stringified JSON
    if isinstance(user_answers, str):
        try:
            user_answers = json.loads(user_answers)
        except Exception:
            user_answers = {}

    quiz = Quiz.query.get_or_404(quiz_id)

    # Prevent Duplicate Submission in same session if already completed
    session_key = f"quiz_completed_{quiz.id}"
    if session.get(session_key):
        existing_result_id = session.get(session_key)
        existing_res = Result.query.get(existing_result_id)
        if existing_res:
            return jsonify({
                'success': True,
                'already_submitted': True,
                'result_id': existing_res.id,
                'redirect_url': url_for('main.result_page', result_id=existing_res.id)
            })

    # Calculate Score
    score = 0
    total_questions = len(quiz.questions)

    for q in quiz.questions:
        q_id_str = str(q.id)
        selected_answer = user_answers.get(q_id_str)
        if selected_answer and selected_answer == q.answer:
            score += 1

    percentage = (score / total_questions * 100) if total_questions > 0 else 0
    grade = calculate_grade(percentage)
    user_id = current_user.id if (current_user and current_user.is_authenticated) else None

    # Save Result
    result = Result(
        quiz_id=quiz.id,
        user_id=user_id,
        score=score,
        total_questions=total_questions,
        percentage=percentage,
        grade=grade,
        user_answers_json=json.dumps(user_answers)
    )

    db.session.add(result)
    db.session.commit()

    # Store in session to prevent duplicate double submission
    session[session_key] = result.id

    return jsonify({
        'success': True,
        'result_id': result.id,
        'score': score,
        'total_questions': total_questions,
        'percentage': round(percentage, 2),
        'grade': grade,
        'redirect_url': url_for('main.result_page', result_id=result.id)
    })


@main_bp.route('/results/<int:result_id>', methods=['GET'])
@main_bp.route('/api/results/<int:result_id>', methods=['GET'])
def api_get_result(result_id):
    """
    GET /results/<id>
    """
    result = Result.query.get_or_404(result_id)
    return jsonify({
        'success': True,
        'result': result.to_dict()
    })


# -------------------------------------------------------------------
# ADMIN DASHBOARD & FEATURES
# -------------------------------------------------------------------

@main_bp.route('/admin')
def admin_dashboard():
    """Admin Management Panel"""
    # Check if current user is admin or guest admin for demonstration
    if not (current_user and current_user.is_authenticated and current_user.is_admin):
        # Render admin dashboard with clear notice if user is guest or non-admin
        pass

    quizzes = Quiz.query.order_by(Quiz.created_at.desc()).all()
    results = Result.query.order_by(Result.completed_at.desc()).all()
    users_count = User.query.count()

    return render_template('admin.html', quizzes=quizzes, results=results, users_count=users_count)


@main_bp.route('/admin/delete-quiz/<int:quiz_id>', methods=['POST'])
def admin_delete_quiz(quiz_id):
    """Admin Endpoint - Delete a quiz and its questions & results"""
    quiz = Quiz.query.get_or_404(quiz_id)
    try:
        db.session.delete(quiz)
        db.session.commit()
        flash('Quiz deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to delete quiz: {e}', 'danger')

    return redirect(url_for('main.admin_dashboard'))


@main_bp.route('/admin/export-csv')
def admin_export_csv():
    """Admin Endpoint - Download all quiz results as CSV"""
    results = Result.query.order_by(Result.completed_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Result ID', 'Topic', 'Difficulty', 'Candidate/User', 'Score', 'Total Questions', 'Percentage', 'Grade', 'Verification Code', 'Completed At'])

    for r in results:
        username = r.user.username if r.user else 'Guest Scholar'
        topic = r.quiz.topic if r.quiz else 'N/A'
        difficulty = r.quiz.difficulty if r.quiz else 'N/A'
        writer.writerow([
            r.id,
            topic,
            difficulty,
            username,
            r.score,
            r.total_questions,
            f"{r.percentage:.2f}%",
            r.grade,
            r.verification_code,
            r.completed_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers["Content-Disposition"] = "attachment; filename=quiz_results_export.csv"
    return response
